"""Interpréteur Applesoft BASIC.

Parcourt l'AST et exécute les instructions. Gère le flux d'exécution,
l'évaluation des expressions, et le compteur d'instructions (ADR-003).
"""

from __future__ import annotations

import math

from . import ast_nodes as ast
from .debug import DebugTracer
from .environment import Environment
from .errors import BasicError
from .formatter import format_number
from .graphics import GraphicsEngine
from .io_cli import IOBridgeCLI
from .memory import MemoryMap
from .parser import parse_tokens
from .program import Program


class BreakInterrupt(Exception):
    """Signal pour interruption Ctrl+C (UC-024)."""


class StopExecution(Exception):
    """Signal pour STOP."""


class EndExecution(Exception):
    """Signal pour END."""


class GotoSignal(Exception):
    """Signal pour GOTO."""

    def __init__(self, target: int):
        self.target = target
        super().__init__()


class GosubSignal(Exception):
    """Signal pour GOSUB — saute et empile le retour."""

    def __init__(self, target: int):
        self.target = target
        super().__init__()


class ReturnSignal(Exception):
    """Signal pour RETURN — dépile et revient."""

    def __init__(self, line_num: int, stmt_idx: int):
        self.line_num = line_num
        self.stmt_idx = stmt_idx
        super().__init__()


class NextLoopSignal(Exception):
    """Signal pour retour au FOR depuis NEXT."""

    def __init__(self, line_num: int, stmt_idx: int):
        self.line_num = line_num
        self.stmt_idx = stmt_idx
        super().__init__()


class OnerrGotoSignal(Exception):
    """Signal pour sauter au handler ONERR GOTO."""

    def __init__(self, target: int):
        self.target = target
        super().__init__()


class ResumeSignal(Exception):
    """Signal pour RESUME — reprend à l'instruction fautive."""

    def __init__(self, line_num: int, stmt_idx: int):
        self.line_num = line_num
        self.stmt_idx = stmt_idx
        super().__init__()


class YieldSignal(Exception):
    """Signal de yield pour le time-slicing (ADR-003, RG-0015).

    Levé quand le compteur d'instructions atteint le seuil de yield.
    Le runner (CLI ou web) catch ce signal et reprend l'exécution via
    resume_execution(). En mode CLI (seuil = inf), jamais levé.
    """

    def __init__(self, line_num: int, stmt_idx: int):
        self.line_num = line_num
        self.stmt_idx = stmt_idx
        super().__init__()


class InputRequestSignal(Exception):
    """Signal levé quand l'Interpreter a besoin d'une entrée utilisateur (INPUT/GET).

    En mode web, le runner doit yield au navigateur et attendre un événement
    clavier/saisie avant de reprendre l'exécution.
    """

    def __init__(self, line_num: int, stmt_idx: int, kind: str, prompt: str = ""):
        self.line_num = line_num
        self.stmt_idx = stmt_idx
        self.kind = kind  # "input" ou "get"
        self.prompt = prompt
        super().__init__()


class Interpreter:
    """Interpréteur Applesoft BASIC."""

    def __init__(
        self,
        program: Program,
        env: Environment,
        io: IOBridgeCLI,
        memory: MemoryMap | None = None,
        debug: DebugTracer | None = None,
        graphics: GraphicsEngine | None = None,
    ):
        self.program = program
        self.env = env
        self.io = io
        self.memory = memory or MemoryMap(env, io)
        self.debug = debug or DebugTracer()
        self.graphics = graphics or GraphicsEngine()
        self._instruction_count = 0
        self._yield_threshold = float("inf")  # Phase 1 : pas de yield
        self._resumed_from: tuple[int, int] | None = None  # Protection anti-boucle RESUME
        self._pending_input_stmt = None  # Pour reprendre après INPUT/GET en mode web

    def set_yield_threshold(self, threshold: int | float) -> None:
        """Configure le seuil de yield (nombre d'instructions par tranche).

        En mode CLI, laisser à float('inf') (pas de yield).
        En mode web, utiliser une valeur finie (ex: 1000) pour le time-slicing.
        """
        self._yield_threshold = threshold

    def get_yield_threshold(self) -> int | float:
        """Retourne le seuil de yield courant."""
        return self._yield_threshold

    def run(self, start_line: int | None = None) -> None:
        """Exécute le programme depuis start_line (ou la première ligne)."""
        self.env.reset()
        self.env.clear_cont()

        # Collecter les DATA
        self._collect_data()

        if start_line is not None:
            if not self.program.has_line(start_line):
                raise BasicError(90)  # UNDEF'D STATEMENT
            current_line = start_line
        else:
            current_line = self.program.first_line_number()
            if current_line is None:
                return  # Programme vide

        self._execute_from(current_line, 0)

    def continue_execution(self) -> None:
        """Reprend l'exécution après STOP/END (CONT)."""
        point = self.env.get_cont_point()
        if point is None:
            raise BasicError(254)  # CAN'T CONTINUE
        line_num, stmt_idx = point
        self.env.clear_cont()
        self._execute_from(line_num, stmt_idx)

    def resume_execution(self, line_num: int, stmt_idx: int) -> None:
        """Reprend l'exécution après un YieldSignal (time-slicing).

        Appelé par le runner web pour reprendre après un yield.
        Réinitialise le compteur d'instructions pour la prochaine tranche.
        """
        self._instruction_count = 0
        self._execute_from(line_num, stmt_idx)

    def resume_after_input(self, line_num: int, stmt_idx: int, value: str) -> None:
        """Reprend l'exécution après réception d'une entrée utilisateur (INPUT/GET).

        Applique la valeur reçue à l'instruction INPUT/GET en attente,
        puis reprend l'exécution à l'instruction suivante.
        """
        self._instruction_count = 0

        # Récupérer l'instruction en attente
        stmt = self._pending_input_stmt
        self._pending_input_stmt = None

        if stmt is not None:
            if isinstance(stmt, ast.GetStmt):
                # GET : assigner le caractère
                if isinstance(stmt.variable, ast.Variable):
                    if stmt.variable.name.endswith("$"):
                        self.env.set_var(stmt.variable.name, value)
                    else:
                        self.env.set_var(
                            stmt.variable.name,
                            float(ord(value)) if value else 0.0,
                        )
            elif isinstance(stmt, ast.InputStmt):
                # INPUT : parser et assigner les valeurs
                parts = value.split(",")
                for i, var_ref in enumerate(stmt.variables):
                    val = parts[i].strip() if i < len(parts) else ""
                    if isinstance(var_ref, ast.Variable):
                        if var_ref.name.endswith("$"):
                            self.env.set_var(var_ref.name, val)
                        else:
                            try:
                                self.env.set_var(var_ref.name, float(val))
                            except ValueError:
                                self.env.set_var(var_ref.name, 0.0)

        # Reprendre à l'instruction suivante
        self._execute_from(line_num, stmt_idx)

    def execute_direct(self, stmt_list: ast.StatementList) -> None:
        """Exécute des instructions en mode direct."""
        for stmt in stmt_list.statements:
            self._exec_stmt(stmt)

    def _collect_data(self) -> None:
        """Collecte toutes les valeurs DATA du programme."""
        all_data = self.program.collect_data()
        values = []
        for _, data_values in all_data:
            values.extend(data_values)
        self.env.set_data_values(values)

    def _next_position(self, line_num: int, stmt_idx: int) -> tuple[int, int]:
        """Calcule la position de l'instruction suivante (ligne, index).

        Utilisé par InputRequestSignal pour indiquer où reprendre après
        réception de la saisie utilisateur.
        """
        line = self.program.get_line(line_num)
        if line is None:
            return (line_num, stmt_idx + 1)
        # Parser si pas en cache
        if line.ast_cache is None:
            stmt_list = parse_tokens(line.tokens, line_num)
            self.program.cache_ast(line_num, stmt_list)
        else:
            stmt_list = line.ast_cache
        if stmt_idx + 1 < len(stmt_list.statements):
            return (line_num, stmt_idx + 1)
        # Passer à la ligne suivante
        next_line = self.program.next_line_number(line_num)
        if next_line is not None:
            return (next_line, 0)
        return (line_num, stmt_idx + 1)  # Fin de programme

    def _execute_from(self, line_num: int, stmt_idx: int) -> None:
        """Exécute le programme à partir d'une ligne et d'un index d'instruction."""
        current_line = line_num

        while current_line is not None:
            line = self.program.get_line(current_line)
            if line is None:
                break

            # Parser si pas en cache
            if line.ast_cache is None:
                stmt_list = parse_tokens(line.tokens, current_line)
                self.program.cache_ast(current_line, stmt_list)
            else:
                stmt_list = line.ast_cache

            # Exécuter les instructions de la ligne
            stmts = stmt_list.statements
            i = stmt_idx
            stmt_idx = 0  # Reset pour les lignes suivantes

            while i < len(stmts):
                stmt = stmts[i]
                self._instruction_count += 1

                # Vérification interruption Ctrl+C (UC-024, ADR-003)
                if self.io.check_interrupt():
                    self.io.print_str(f"BREAK IN {current_line}\n")
                    # Sauvegarder le point de reprise pour CONT
                    self.env.save_cont_point(current_line, i)
                    return

                # Time-slicing : yield au navigateur (ADR-003, RG-0015)
                if self._instruction_count >= self._yield_threshold:
                    self._instruction_count = 0
                    raise YieldSignal(current_line, i)

                # Trace debug
                if self.debug.enabled:
                    self.debug.trace(current_line, type(stmt).__name__)

                try:
                    # Stocker la position courante pour GOSUB et FOR
                    self._current_line = current_line
                    self._current_stmt_idx = i
                    self._exec_stmt(stmt)
                except GotoSignal as g:
                    current_line = g.target
                    if not self.program.has_line(current_line):
                        raise BasicError(90, current_line) from None
                    break
                except GosubSignal as g:
                    # Empiler le retour (instruction suivante)
                    if i + 1 < len(stmts):
                        self.env.push_gosub(current_line, i + 1)
                    else:
                        nxt = self.program.next_line_number(current_line)
                        self.env.push_gosub(nxt if nxt else -1, 0)
                    current_line = g.target
                    if not self.program.has_line(current_line):
                        raise BasicError(90, current_line) from None
                    break
                except ReturnSignal as r:
                    current_line = r.line_num
                    stmt_idx = r.stmt_idx
                    break
                except NextLoopSignal as n:
                    current_line = n.line_num
                    stmt_idx = n.stmt_idx
                    break
                except StopExecution:
                    self.io.print_str(f"BREAK IN {current_line}\n")
                    if i + 1 < len(stmts):
                        self.env.save_cont_point(current_line, i + 1)
                    else:
                        next_line = self.program.next_line_number(current_line)
                        if next_line is not None:
                            self.env.save_cont_point(next_line, 0)
                    return
                except EndExecution:
                    if i + 1 < len(stmts):
                        self.env.save_cont_point(current_line, i + 1)
                    else:
                        next_line = self.program.next_line_number(current_line)
                        if next_line is not None:
                            self.env.save_cont_point(next_line, 0)
                    return
                except OnerrGotoSignal as o:
                    current_line = o.target
                    if not self.program.has_line(current_line):
                        raise BasicError(90, current_line) from None
                    self.env.set_onerr_active(True)
                    break
                except ResumeSignal as r:
                    current_line = r.line_num
                    stmt_idx = r.stmt_idx
                    self.env.set_onerr_active(False)
                    self._resumed_from = (r.line_num, r.stmt_idx)
                    break
                except BasicError as e:
                    if e.line_number is None:
                        e.line_number = current_line
                    # ONERR GOTO actif ?
                    target = self.env.get_onerr_target()
                    if target is not None:
                        # Protection anti-boucle : erreur dans le handler
                        if self.env.is_onerr_active():
                            self.env.set_onerr_active(False)
                            raise
                        # Protection anti-boucle : RESUME revient sur la même erreur
                        if self._resumed_from == (current_line, i):
                            self._resumed_from = None
                            self.env.set_onerr_active(False)
                            raise
                        self._resumed_from = None
                        # Stocker le code et la ligne d'erreur
                        self.env.set_error_code(e.code)
                        self.env.set_error_line(current_line)
                        # Sauvegarder le point de reprise pour RESUME
                        self.env.set_resume_point(current_line, i)
                        # Sauter au handler
                        self.env.set_onerr_active(True)
                        current_line = target
                        if not self.program.has_line(current_line):
                            self.env.set_onerr_active(False)
                            raise BasicError(90, current_line) from None
                        stmt_idx = 0
                        break
                    raise

                i += 1
            else:
                # Passer à la ligne suivante
                current_line = self.program.next_line_number(current_line)
                continue

    # --- Exécution des instructions ---

    def _exec_stmt(self, stmt: object) -> None:
        """Exécute une instruction."""
        if isinstance(stmt, ast.LetStmt):
            self._exec_let(stmt)
        elif isinstance(stmt, ast.PrintStmt):
            self._exec_print(stmt)
        elif isinstance(stmt, ast.DimStmt):
            self._exec_dim(stmt)
        elif isinstance(stmt, ast.RemStmt):
            pass  # No-op
        elif isinstance(stmt, ast.EndStmt):
            raise EndExecution
        elif isinstance(stmt, ast.StopStmt):
            raise StopExecution
        elif isinstance(stmt, ast.GotoStmt):
            raise GotoSignal(stmt.target)
        elif isinstance(stmt, ast.GosubStmt):
            self._exec_gosub(stmt)
        elif isinstance(stmt, ast.ReturnStmt):
            self._exec_return()
        elif isinstance(stmt, ast.ForStmt):
            self._exec_for(stmt)
        elif isinstance(stmt, ast.NextStmt):
            self._exec_next(stmt)
        elif isinstance(stmt, ast.IfStmt):
            self._exec_if(stmt)
        elif isinstance(stmt, ast.OnGotoStmt):
            self._exec_on_goto(stmt)
        elif isinstance(stmt, ast.OnGosubStmt):
            self._exec_on_gosub(stmt)
        elif isinstance(stmt, ast.DataStmt):
            pass  # DATA est collecté au début, pas exécuté
        elif isinstance(stmt, ast.ReadStmt):
            self._exec_read(stmt)
        elif isinstance(stmt, ast.RestoreStmt):
            self.env.restore()
        elif isinstance(stmt, ast.DefFnStmt):
            self.env.def_fn(stmt.name, stmt.param, stmt.body)
        elif isinstance(stmt, ast.PopStmt):
            self.env.pop_gosub()
        elif isinstance(stmt, ast.HomeStmt):
            self.io.clear_screen()
        elif isinstance(stmt, ast.ClearStmt):
            self.env.reset()
        elif isinstance(stmt, ast.InputStmt):
            self._exec_input(stmt)
        elif isinstance(stmt, ast.GetStmt):
            self._exec_get(stmt)
        elif isinstance(stmt, ast.RunStmt):
            pass  # Géré par le REPL
        elif isinstance(stmt, ast.ListStmt):
            pass  # Géré par le REPL
        elif isinstance(stmt, ast.NewStmt):
            pass  # Géré par le REPL
        elif isinstance(stmt, ast.DelStmt):
            pass  # Géré par le REPL
        elif isinstance(stmt, ast.ContStmt):
            pass  # Géré par le REPL
        elif isinstance(stmt, ast.HtabStmt):
            self._exec_htab(stmt)
        elif isinstance(stmt, ast.VtabStmt):
            self._exec_vtab(stmt)
        elif isinstance(stmt, ast.NormalStmt):
            self.io.set_video_mode("normal")
        elif isinstance(stmt, ast.InverseStmt):
            self.io.set_video_mode("inverse")
        elif isinstance(stmt, ast.FlashStmt):
            self.io.set_video_mode("flash")
        elif isinstance(stmt, ast.SpeedStmt):
            self._exec_speed(stmt)
        elif isinstance(stmt, ast.TextStmt):
            self.graphics.text()
        elif isinstance(stmt, ast.PokeStmt):
            self._exec_poke(stmt)
        elif isinstance(stmt, ast.CallStmt):
            self._exec_call(stmt)
        elif isinstance(stmt, ast.GrStmt):
            self.graphics.gr()
        elif isinstance(stmt, ast.ColorStmt):
            self._exec_color(stmt)
        elif isinstance(stmt, ast.PlotStmt):
            self._exec_plot(stmt)
        elif isinstance(stmt, ast.HlinStmt):
            self._exec_hlin(stmt)
        elif isinstance(stmt, ast.VlinStmt):
            self._exec_vlin(stmt)
        elif isinstance(stmt, ast.HgrStmt):
            self.graphics.hgr()
        elif isinstance(stmt, ast.Hgr2Stmt):
            self.graphics.hgr2()
        elif isinstance(stmt, ast.HcolorStmt):
            self._exec_hcolor(stmt)
        elif isinstance(stmt, ast.HplotStmt):
            self._exec_hplot(stmt)
        elif isinstance(stmt, ast.DrawStmt):
            self._exec_draw(stmt)
        elif isinstance(stmt, ast.XdrawStmt):
            self._exec_xdraw(stmt)
        elif isinstance(stmt, ast.RotStmt):
            self._exec_rot(stmt)
        elif isinstance(stmt, ast.ScaleStmt):
            self._exec_scale(stmt)
        elif isinstance(stmt, ast.OnerrStmt):
            self._exec_onerr(stmt)
        elif isinstance(stmt, ast.ResumeStmt):
            self._exec_resume()

    def _exec_let(self, stmt: ast.LetStmt) -> None:
        """Exécute une assignation LET."""
        value = self._eval(stmt.value)
        self._assign(stmt.target, value)

    def _assign(self, target: object, value: object) -> None:
        """Assigne une valeur à une variable ou un tableau."""
        if isinstance(target, ast.Variable):
            self.env.set_var(target.name, value)
        elif isinstance(target, ast.ArrayAccess):
            indices = [int(self._eval(idx)) for idx in target.indices]
            self.env.set_array(target.name, indices, value)

    def _exec_print(self, stmt: ast.PrintStmt) -> None:
        """Exécute PRINT (UC-006)."""
        last_sep = None

        for item_tuple in stmt.items:
            item, sep = item_tuple

            if item is not None:
                if isinstance(item, ast.SpcCall):
                    count = int(self._eval(item.count))
                    if count < 0:
                        raise BasicError(53)  # ILLEGAL QUANTITY
                    self.io.print_str(" " * count)
                elif isinstance(item, ast.TabCall):
                    col = int(self._eval(item.column))
                    if col < 1:
                        raise BasicError(53)  # ILLEGAL QUANTITY
                    current = self.io.get_cursor_column()
                    if current > col:
                        # Passer à la ligne suivante (CA-UC-006-09)
                        self.io.print_str("\n")
                        self.io.print_str(" " * (col - 1))
                    else:
                        self.io.print_str(" " * (col - current))
                else:
                    value = self._eval(item)
                    if isinstance(value, str):
                        self.io.print_str(value)
                    else:
                        self.io.print_str(format_number(value))

            # Appliquer le séparateur
            if sep == ",":
                # Avancer au prochain tabulateur 16 colonnes
                current = self.io.get_cursor_column()
                next_tab = ((current - 1) // 16 + 1) * 16 + 1
                self.io.print_str(" " * (next_tab - current))
            # ';' = pas d'espace (concaténation)

            last_sep = sep

        # Fin de PRINT : retour à la ligne sauf si terminé par ; ou ,
        if last_sep is None:
            self.io.print_str("\n")

    def _exec_dim(self, stmt: ast.DimStmt) -> None:
        """Exécute DIM."""
        for name, dim_exprs in stmt.declarations:
            dims = [int(self._eval(d)) for d in dim_exprs]
            self.env.dim_array(name, dims)

    def _exec_gosub(self, stmt: ast.GosubStmt) -> None:
        """Exécute GOSUB — empile le retour et saute."""
        raise GosubSignal(stmt.target)

    def _exec_return(self) -> None:
        """Exécute RETURN — dépile et revient après le GOSUB."""
        line_num, stmt_idx = self.env.pop_gosub()
        raise ReturnSignal(line_num, stmt_idx)

    def _exec_for(self, stmt: ast.ForStmt) -> None:
        """Exécute FOR — initialise la variable et empile le contexte de boucle."""
        start_val = self._eval_numeric(stmt.start)
        end_val = self._eval_numeric(stmt.end)
        step_val = 1.0 if stmt.step is None else self._eval_numeric(stmt.step)
        self.env.set_var(stmt.var_name, start_val)
        # Sauver le contexte pour NEXT : revenir à l'instruction suivant le FOR
        self.env.push_for(
            {
                "var": stmt.var_name,
                "end": end_val,
                "step": step_val,
                "line": self._current_line,
                "stmt_idx": self._current_stmt_idx + 1,
            }
        )

    def _exec_next(self, stmt: ast.NextStmt) -> None:
        """Exécute NEXT — incrémente et boucle ou continue."""
        var_names = stmt.var_names if stmt.var_names else [None]
        for var_name in var_names:
            self._do_next(var_name)

    def _do_next(self, var_name: str | None) -> None:
        """Traite un NEXT pour une variable."""
        info = self.env.peek_for(var_name)
        actual_var = info["var"]
        end_val = info["end"]
        step_val = info["step"]

        # Incrémenter
        current = self.env.get_var(actual_var)
        current += step_val
        self.env.set_var(actual_var, current)

        # Tester la condition de fin
        if step_val >= 0:
            done = current > end_val
        else:
            done = current < end_val

        if done:
            # Boucle terminée — dépiler
            self.env.pop_for(actual_var)
        else:
            # Continuer la boucle — revenir après le FOR
            raise NextLoopSignal(info["line"], info["stmt_idx"])

    def _exec_if(self, stmt: ast.IfStmt) -> None:
        """Exécute IF/THEN/ELSE."""
        condition = self._eval(stmt.condition)
        if _is_truthy(condition):
            for s in stmt.then_clause:
                self._exec_stmt(s)
        elif stmt.else_clause:
            for s in stmt.else_clause:
                self._exec_stmt(s)

    def _exec_on_goto(self, stmt: ast.OnGotoStmt) -> None:
        """Exécute ON...GOTO."""
        idx = int(self._eval_numeric(stmt.expr))
        if idx < 0:
            raise BasicError(53)  # ILLEGAL QUANTITY
        if 1 <= idx <= len(stmt.targets):
            raise GotoSignal(stmt.targets[idx - 1])
        # Valeur hors plage : continue à l'instruction suivante

    def _exec_on_gosub(self, stmt: ast.OnGosubStmt) -> None:
        """Exécute ON...GOSUB."""
        idx = int(self._eval_numeric(stmt.expr))
        if idx < 0:
            raise BasicError(53)  # ILLEGAL QUANTITY
        if 1 <= idx <= len(stmt.targets):
            raise GosubSignal(stmt.targets[idx - 1])

    def _exec_read(self, stmt: ast.ReadStmt) -> None:
        """Exécute READ."""
        for var_ref in stmt.variables:
            raw = self.env.read_data()
            if isinstance(var_ref, ast.Variable):
                if var_ref.name.endswith("$"):
                    self.env.set_var(var_ref.name, raw)
                else:
                    try:
                        self.env.set_var(var_ref.name, float(raw))
                    except ValueError:
                        self.env.set_var(var_ref.name, 0.0)

    def _exec_input(self, stmt: ast.InputStmt) -> None:
        """Exécute INPUT.

        En mode web (yield_threshold fini), lève InputRequestSignal pour
        demander une saisie asynchrone au lieu de bloquer.
        """
        prompt = stmt.prompt if stmt.prompt else "?"
        if not prompt.endswith("?"):
            prompt += "?"

        # Mode web : lever un signal pour saisie asynchrone
        if self._yield_threshold != float("inf"):
            self.io.print_str(prompt)
            self._pending_input_stmt = stmt
            # Reprendre à l'instruction SUIVANTE après réception de la saisie
            next_line, next_idx = self._next_position(self._current_line, self._current_stmt_idx)
            raise InputRequestSignal(next_line, next_idx, "input", prompt)

        # Mode CLI : lecture synchrone
        line = self.io.input_str(prompt)
        parts = line.split(",")
        for i, var_ref in enumerate(stmt.variables):
            val = parts[i].strip() if i < len(parts) else ""
            if isinstance(var_ref, ast.Variable):
                if var_ref.name.endswith("$"):
                    self.env.set_var(var_ref.name, val)
                else:
                    try:
                        self.env.set_var(var_ref.name, float(val))
                    except ValueError:
                        self.env.set_var(var_ref.name, 0.0)

    def _exec_get(self, stmt: ast.GetStmt) -> None:
        """Exécute GET.

        En mode web (yield_threshold fini), lève InputRequestSignal pour
        capturer une touche de manière asynchrone au lieu de bloquer.
        """
        # Mode web : lever un signal pour capture clavier asynchrone
        if self._yield_threshold != float("inf"):
            self._pending_input_stmt = stmt
            next_line, next_idx = self._next_position(self._current_line, self._current_stmt_idx)
            raise InputRequestSignal(next_line, next_idx, "get", "")

        # Mode CLI : lecture synchrone
        ch = self.io.get_char()
        if isinstance(stmt.variable, ast.Variable):
            if stmt.variable.name.endswith("$"):
                self.env.set_var(stmt.variable.name, ch)
            else:
                self.env.set_var(stmt.variable.name, float(ord(ch)) if ch else 0.0)

    def _exec_htab(self, stmt: ast.HtabStmt) -> None:
        """Exécute HTAB."""
        col = int(self._eval_numeric(stmt.column))
        if col < 1 or col > 40:
            raise BasicError(53)  # ILLEGAL QUANTITY
        current = self.io.get_cursor_column()
        if col > current:
            self.io.print_str(" " * (col - current))

    def _exec_vtab(self, stmt: ast.VtabStmt) -> None:
        """Exécute VTAB (UC-009)."""
        row = int(self._eval_numeric(stmt.row))
        if row < 1 or row > 24:
            raise BasicError(53)  # ILLEGAL QUANTITY
        self.io.move_cursor_to_row(row)

    def _exec_speed(self, stmt: ast.SpeedStmt) -> None:
        """Exécute SPEED= (UC-009)."""
        value = int(self._eval_numeric(stmt.value))
        if value < 0 or value > 255:
            raise BasicError(53)  # ILLEGAL QUANTITY
        self.io.set_speed(value)

    def _exec_onerr(self, stmt: ast.OnerrStmt) -> None:
        """Exécute ONERR GOTO linenum (UC-023)."""
        if stmt.target == 0:
            self.env.set_onerr_target(None)
        else:
            self.env.set_onerr_target(stmt.target)
        self.env.set_onerr_active(False)

    def _exec_resume(self) -> None:
        """Exécute RESUME (UC-023)."""
        point = self.env.get_resume_point()
        if point is None:
            raise BasicError(16)  # SYNTAX ERROR
        line_num, stmt_idx = point
        raise ResumeSignal(line_num, stmt_idx)

    # --- Graphisme (UC-018, UC-019, UC-020) ---

    def _exec_color(self, stmt: ast.ColorStmt) -> None:
        """Exécute COLOR= n (UC-018)."""
        value = int(self._eval_numeric(stmt.value))
        try:
            self.graphics.set_color(value)
        except ValueError:
            raise BasicError(53) from None

    def _exec_plot(self, stmt: ast.PlotStmt) -> None:
        """Exécute PLOT x,y (UC-018)."""
        x = int(self._eval_numeric(stmt.x))
        y = int(self._eval_numeric(stmt.y))
        try:
            self.graphics.plot(x, y)
        except ValueError:
            raise BasicError(53) from None

    def _exec_hlin(self, stmt: ast.HlinStmt) -> None:
        """Exécute HLIN x1,x2 AT y (UC-018)."""
        x1 = int(self._eval_numeric(stmt.x1))
        x2 = int(self._eval_numeric(stmt.x2))
        y = int(self._eval_numeric(stmt.y))
        try:
            self.graphics.hlin(x1, x2, y)
        except ValueError:
            raise BasicError(53) from None

    def _exec_vlin(self, stmt: ast.VlinStmt) -> None:
        """Exécute VLIN y1,y2 AT x (UC-018)."""
        y1 = int(self._eval_numeric(stmt.y1))
        y2 = int(self._eval_numeric(stmt.y2))
        x = int(self._eval_numeric(stmt.x))
        try:
            self.graphics.vlin(y1, y2, x)
        except ValueError:
            raise BasicError(53) from None

    def _exec_hcolor(self, stmt: ast.HcolorStmt) -> None:
        """Exécute HCOLOR= n (UC-019)."""
        value = int(self._eval_numeric(stmt.value))
        try:
            self.graphics.set_hcolor(value)
        except ValueError:
            raise BasicError(53) from None

    def _exec_hplot(self, stmt: ast.HplotStmt) -> None:
        """Exécute HPLOT (UC-019)."""
        points = stmt.points
        if stmt.from_last:
            # HPLOT TO x,y — depuis la dernière position
            for px, py in points:
                x = int(self._eval_numeric(px))
                y = int(self._eval_numeric(py))
                try:
                    self.graphics.hplot_to(x, y)
                except ValueError:
                    raise BasicError(53) from None
        else:
            # Premier point
            px0, py0 = points[0]
            x0 = int(self._eval_numeric(px0))
            y0 = int(self._eval_numeric(py0))
            try:
                self.graphics.hplot_point(x0, y0)
            except ValueError:
                raise BasicError(53) from None
            # Segments suivants (TO)
            for px, py in points[1:]:
                x = int(self._eval_numeric(px))
                y = int(self._eval_numeric(py))
                try:
                    self.graphics.hplot_to(x, y)
                except ValueError:
                    raise BasicError(53) from None

    def _exec_draw(self, stmt: ast.DrawStmt) -> None:
        """Exécute DRAW n AT x,y (UC-020)."""
        shape = int(self._eval_numeric(stmt.shape))
        x = int(self._eval_numeric(stmt.x))
        y = int(self._eval_numeric(stmt.y))
        try:
            self.graphics.draw_shape(shape, x, y)
        except ValueError:
            raise BasicError(53) from None

    def _exec_xdraw(self, stmt: ast.XdrawStmt) -> None:
        """Exécute XDRAW n AT x,y (UC-020)."""
        shape = int(self._eval_numeric(stmt.shape))
        x = int(self._eval_numeric(stmt.x))
        y = int(self._eval_numeric(stmt.y))
        try:
            self.graphics.xdraw_shape(shape, x, y)
        except ValueError:
            raise BasicError(53) from None

    def _exec_rot(self, stmt: ast.RotStmt) -> None:
        """Exécute ROT= n (UC-020)."""
        value = int(self._eval_numeric(stmt.value))
        try:
            self.graphics.set_rot(value)
        except ValueError:
            raise BasicError(53) from None

    def _exec_scale(self, stmt: ast.ScaleStmt) -> None:
        """Exécute SCALE= n (UC-020)."""
        value = int(self._eval_numeric(stmt.value))
        try:
            self.graphics.set_scale(value)
        except ValueError:
            raise BasicError(53) from None

    def _exec_poke(self, stmt: ast.PokeStmt) -> None:
        """Exécute POKE addr, val (UC-022)."""
        addr = int(self._eval_numeric(stmt.address))
        val = int(self._eval_numeric(stmt.value))
        self.memory.poke(addr, val)

    def _exec_call(self, stmt: ast.CallStmt) -> None:
        """Exécute CALL addr (UC-022)."""
        addr = int(self._eval_numeric(stmt.address))
        self.memory.call(addr)

    # --- Évaluation des expressions ---

    def _eval(self, expr: object) -> float | int | str:
        """Évalue une expression AST et retourne sa valeur."""
        if isinstance(expr, ast.NumberLiteral):
            return expr.value

        if isinstance(expr, ast.StringLiteral):
            return expr.value

        if isinstance(expr, ast.Variable):
            return self.env.get_var(expr.name)

        if isinstance(expr, ast.ArrayAccess):
            indices = [int(self._eval(idx)) for idx in expr.indices]
            return self.env.get_array(expr.name, indices)

        if isinstance(expr, ast.ParenExpr):
            return self._eval(expr.expr)

        if isinstance(expr, ast.UnaryOp):
            return self._eval_unary(expr)

        if isinstance(expr, ast.BinaryOp):
            return self._eval_binary(expr)

        if isinstance(expr, ast.FunctionCall):
            return self._eval_function(expr)

        if isinstance(expr, ast.FnCall):
            return self._eval_fn_call(expr)

        if isinstance(expr, ast.PeekExpr):
            addr = int(self._eval_numeric(expr.address))
            return self.memory.peek(addr)

        if isinstance(expr, ast.ScrnExpr):
            x = int(self._eval_numeric(expr.x))
            y = int(self._eval_numeric(expr.y))
            try:
                return self.graphics.scrn(x, y)
            except ValueError:
                raise BasicError(53) from None

        if isinstance(expr, ast.PosExpr):
            self._eval(expr.arg)  # Évalué mais ignoré
            return self.io.get_cursor_column()

        if isinstance(expr, ast.SpcCall):
            return expr  # Géré par PRINT

        if isinstance(expr, ast.TabCall):
            return expr  # Géré par PRINT

        raise BasicError(16)  # SYNTAX ERROR

    def _eval_numeric(self, expr: object) -> float:
        """Évalue une expression et vérifie qu'elle est numérique."""
        value = self._eval(expr)
        if isinstance(value, str):
            raise BasicError(163)  # TYPE MISMATCH
        return float(value)

    def _eval_unary(self, expr: ast.UnaryOp) -> float | int:
        """Évalue un opérateur unaire."""
        operand = self._eval(expr.operand)
        if expr.op == "-":
            if isinstance(operand, str):
                raise BasicError(163)
            return -operand
        if expr.op == "+":
            if isinstance(operand, str):
                raise BasicError(163)
            return operand
        if expr.op == "NOT":
            if isinstance(operand, str):
                raise BasicError(163)
            # NOT booléen : retourne 1 si opérande = 0, sinon 0
            return 1 if operand == 0 else 0
        raise BasicError(16)

    def _eval_binary(self, expr: ast.BinaryOp) -> float | int | str:
        """Évalue un opérateur binaire."""
        left = self._eval(expr.left)
        right = self._eval(expr.right)
        op = expr.op

        # Concaténation de chaînes
        if op == "+" and isinstance(left, str) and isinstance(right, str):
            result = left + right
            if len(result) > 255:
                raise BasicError(176)  # STRING TOO LONG
            return result

        # Comparaisons (supportent chaînes)
        if op in ("=", "<>", "><", "<", ">", "<=", "=<", ">=", "=>"):
            return self._eval_comparison(op, left, right)

        # Opérateurs arithmétiques
        if isinstance(left, str) or isinstance(right, str):
            raise BasicError(163)  # TYPE MISMATCH

        left_f = float(left)
        right_f = float(right)

        if op == "+":
            result = left_f + right_f
        elif op == "-":
            result = left_f - right_f
        elif op == "*":
            result = left_f * right_f
        elif op == "/":
            if right_f == 0:
                raise BasicError(133)  # DIVISION BY ZERO
            result = left_f / right_f
        elif op == "^":
            if left_f == 0 and right_f == 0:
                return 1  # Convention Applesoft : 0^0 = 1
            try:
                result = left_f**right_f
            except (OverflowError, ValueError):
                raise BasicError(69) from None  # OVERFLOW
        elif op == "AND":
            # Bit à bit sur entiers
            return int(left_f) & int(right_f)
        elif op == "OR":
            return int(left_f) | int(right_f)
        else:
            raise BasicError(16)

        # Vérifier overflow
        if math.isinf(result):
            raise BasicError(69)  # OVERFLOW

        return result

    def _eval_comparison(self, op: str, left: float | int | str, right: float | int | str) -> int:
        """Évalue une comparaison et retourne 0 ou 1."""
        # Comparaison entre types identiques
        if isinstance(left, str) and isinstance(right, str):
            cmp_result = (left > right) - (left < right)
        elif isinstance(left, str) or isinstance(right, str):
            raise BasicError(163)  # TYPE MISMATCH
        else:
            left_f = float(left)
            right_f = float(right)
            cmp_result = (left_f > right_f) - (left_f < right_f)

        if op == "=":
            return 1 if cmp_result == 0 else 0
        if op in ("<>", "><"):
            return 1 if cmp_result != 0 else 0
        if op == "<":
            return 1 if cmp_result < 0 else 0
        if op == ">":
            return 1 if cmp_result > 0 else 0
        if op in ("<=", "=<"):
            return 1 if cmp_result <= 0 else 0
        if op in (">=", "=>"):
            return 1 if cmp_result >= 0 else 0
        return 0

    def _eval_function(self, expr: ast.FunctionCall) -> float | int | str:
        """Évalue un appel de fonction intégrée."""
        name = expr.name
        args = [self._eval(a) for a in expr.args]

        # Fonctions mathématiques
        if name == "ABS":
            return abs(self._ensure_numeric(args[0]))
        if name == "INT":
            return float(math.floor(self._ensure_numeric(args[0])))
        if name == "SGN":
            v = self._ensure_numeric(args[0])
            return 1 if v > 0 else (-1 if v < 0 else 0)
        if name == "SQR":
            v = self._ensure_numeric(args[0])
            if v < 0:
                raise BasicError(53)
            return math.sqrt(v)
        if name == "LOG":
            v = self._ensure_numeric(args[0])
            if v <= 0:
                raise BasicError(53)
            return math.log(v)
        if name == "EXP":
            try:
                return math.exp(self._ensure_numeric(args[0]))
            except OverflowError:
                raise BasicError(69) from None
        if name == "SIN":
            return math.sin(self._ensure_numeric(args[0]))
        if name == "COS":
            return math.cos(self._ensure_numeric(args[0]))
        if name == "TAN":
            return math.tan(self._ensure_numeric(args[0]))
        if name == "ATN":
            return math.atan(self._ensure_numeric(args[0]))
        if name == "RND":
            import random

            v = self._ensure_numeric(args[0])
            if v < 0:
                random.seed(int(v))
                self._last_rnd = random.random()
                return self._last_rnd
            if v == 0:
                return getattr(self, "_last_rnd", 0.0)
            self._last_rnd = random.random()
            return self._last_rnd

        # Fonctions de chaînes
        if name == "LEN":
            s = self._ensure_string(args[0])
            return len(s)
        if name == "LEFT$":
            s = self._ensure_string(args[0])
            n = int(self._ensure_numeric(args[1]))
            if n < 0:
                raise BasicError(53)
            return s[:n]
        if name == "RIGHT$":
            s = self._ensure_string(args[0])
            n = int(self._ensure_numeric(args[1]))
            return s[-n:] if n > 0 else ""
        if name == "MID$":
            s = self._ensure_string(args[0])
            start = int(self._ensure_numeric(args[1]))
            if start < 1:
                raise BasicError(53)
            length = len(s) - start + 1
            if len(args) > 2:
                length = int(self._ensure_numeric(args[2]))
                if length < 0:
                    raise BasicError(53)
            return s[start - 1 : start - 1 + length]
        if name == "ASC":
            s = self._ensure_string(args[0])
            if len(s) == 0:
                raise BasicError(53)
            return ord(s[0])
        if name == "CHR$":
            v = int(self._ensure_numeric(args[0]))
            if v < 0 or v > 255:
                raise BasicError(53)
            return chr(v)
        if name == "STR$":
            v = self._ensure_numeric(args[0])
            return format_number(v)
        if name == "VAL":
            s = self._ensure_string(args[0])
            return _parse_val(s)

        raise BasicError(16)

    def _eval_fn_call(self, expr: ast.FnCall) -> float | int | str:
        """Évalue un appel FN."""
        param_name, body = self.env.get_fn(expr.name)
        arg_val = self._eval(expr.arg)
        # Sauver et restaurer le paramètre
        old_val = self.env.get_var(param_name)
        self.env.set_var(param_name, arg_val)
        try:
            result = self._eval(body)
        finally:
            self.env.set_var(param_name, old_val)
        return result

    def _ensure_numeric(self, value: object) -> float:
        if isinstance(value, str):
            raise BasicError(163)
        return float(value)

    def _ensure_string(self, value: object) -> str:
        if not isinstance(value, str):
            raise BasicError(163)
        return value


def _is_truthy(value: object) -> bool:
    """Teste si une valeur est vraie en Applesoft."""
    if isinstance(value, str):
        return len(value) > 0
    return value != 0


def _parse_val(s: str) -> float:
    """Parse une chaîne en nombre pour VAL()."""
    s = s.strip()
    if not s:
        return 0.0
    # Lire autant de caractères numériques que possible
    num_str = ""
    for ch in s:
        if ch.isdigit() or ch in ".+-eE":
            num_str += ch
        elif ch == " ":
            continue
        else:
            break
    if not num_str:
        return 0.0
    try:
        return float(num_str)
    except ValueError:
        return 0.0
