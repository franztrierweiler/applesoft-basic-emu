"""Interpréteur Applesoft BASIC.

Parcourt l'AST et exécute les instructions. Gère le flux d'exécution,
l'évaluation des expressions, et le compteur d'instructions (ADR-003).
"""

from __future__ import annotations

import math

from . import ast_nodes as ast
from .environment import Environment
from .errors import BasicError
from .formatter import format_number
from .io_cli import IOBridgeCLI
from .parser import parse_tokens
from .program import Program


class StopExecution(Exception):
    """Signal pour STOP."""


class EndExecution(Exception):
    """Signal pour END."""


class GotoSignal(Exception):
    """Signal pour GOTO."""

    def __init__(self, target: int):
        self.target = target
        super().__init__()


class Interpreter:
    """Interpréteur Applesoft BASIC."""

    def __init__(
        self,
        program: Program,
        env: Environment,
        io: IOBridgeCLI,
    ):
        self.program = program
        self.env = env
        self.io = io
        self._instruction_count = 0
        self._yield_threshold = float("inf")  # Phase 1 : pas de yield

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

                try:
                    self._exec_stmt(stmt)
                except GotoSignal as g:
                    current_line = g.target
                    if not self.program.has_line(current_line):
                        raise BasicError(90, current_line) from None
                    break
                except StopExecution:
                    self.io.print_str(f"BREAK IN {current_line}\n")
                    # Sauver le point de reprise (instruction suivante)
                    if i + 1 < len(stmts):
                        self.env.save_cont_point(current_line, i + 1)
                    else:
                        next_line = self.program.next_line_number(current_line)
                        if next_line is not None:
                            self.env.save_cont_point(next_line, 0)
                    return
                except EndExecution:
                    # Sauver le point de reprise
                    if i + 1 < len(stmts):
                        self.env.save_cont_point(current_line, i + 1)
                    else:
                        next_line = self.program.next_line_number(current_line)
                        if next_line is not None:
                            self.env.save_cont_point(next_line, 0)
                    return
                except BasicError as e:
                    if e.line_number is None:
                        e.line_number = current_line
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
            pass  # Lot 4
        elif isinstance(stmt, ast.NormalStmt):
            pass  # Lot 4
        elif isinstance(stmt, ast.InverseStmt):
            pass  # Lot 4
        elif isinstance(stmt, ast.FlashStmt):
            pass  # Lot 4
        elif isinstance(stmt, ast.SpeedStmt):
            pass  # Lot 4
        elif isinstance(stmt, ast.TextStmt):
            pass  # Lot 6
        elif isinstance(stmt, ast.PokeStmt):
            pass  # Lot 5
        elif isinstance(stmt, ast.CallStmt):
            pass  # Lot 5
        elif isinstance(stmt, ast.OnerrStmt):
            pass  # Lot 5
        elif isinstance(stmt, ast.ResumeStmt):
            pass  # Lot 5

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
        # Le retour sera géré par le contexte appelant
        raise GotoSignal(stmt.target)

    def _exec_return(self) -> None:
        """Exécute RETURN."""
        line_num, stmt_idx = self.env.pop_gosub()
        # Pas encore implémenté complètement — lot 3
        raise GotoSignal(line_num)

    def _exec_for(self, stmt: ast.ForStmt) -> None:
        """Exécute FOR."""
        start_val = self._eval_numeric(stmt.start)
        # Évaluer end et step pour détecter les erreurs, mais lot 3 implémentera la boucle
        self._eval_numeric(stmt.end)
        if stmt.step is not None:
            self._eval_numeric(stmt.step)
        self.env.set_var(stmt.var_name, start_val)

    def _exec_next(self, stmt: ast.NextStmt) -> None:
        """Exécute NEXT."""
        # Pas encore implémenté complètement — lot 3
        pass

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
        if 1 <= idx <= len(stmt.targets):
            raise GotoSignal(stmt.targets[idx - 1])
        # Sinon, continue à l'instruction suivante

    def _exec_on_gosub(self, stmt: ast.OnGosubStmt) -> None:
        """Exécute ON...GOSUB."""
        idx = int(self._eval_numeric(stmt.expr))
        if 1 <= idx <= len(stmt.targets):
            raise GotoSignal(stmt.targets[idx - 1])

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
        """Exécute INPUT."""
        prompt = stmt.prompt if stmt.prompt else "?"
        if not prompt.endswith("?"):
            prompt += "?"
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
        """Exécute GET."""
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
            # Lot 5
            return 0

        if isinstance(expr, ast.ScrnExpr):
            # Lot 6
            return 0

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
                return random.random()
            if v == 0:
                return random.random()  # Répète le dernier (simplifié)
            return random.random()

        # Fonctions de chaînes
        if name == "LEN":
            s = self._ensure_string(args[0])
            return len(s)
        if name == "LEFT$":
            s = self._ensure_string(args[0])
            n = int(self._ensure_numeric(args[1]))
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
