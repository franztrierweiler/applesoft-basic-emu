"""Boucle REPL Applesoft BASIC.

Gère le prompt `]`, le dispatch mode direct/différé,
et les commandes système (RUN, LIST, NEW, DEL, CONT).
"""

from __future__ import annotations

from . import ast_nodes as ast
from .debug import DebugTracer
from .environment import Environment
from .errors import BasicError
from .graphics import GraphicsEngine
from .interpreter import Interpreter
from .io_cli import IOBridgeCLI
from .lexer import MAX_LINE_NUMBER, Token, TokenType, tokenize
from .memory import MemoryMap
from .parser import parse_tokens
from .program import Program


class REPL:
    """Boucle REPL interactive Applesoft BASIC."""

    def __init__(
        self,
        io: IOBridgeCLI | None = None,
        file_dir: str | None = None,
        debug: DebugTracer | None = None,
    ):
        self.io = io or IOBridgeCLI()
        self.program = Program()
        self.env = Environment()
        self.debug = debug or DebugTracer()
        self.graphics = GraphicsEngine()
        memory = MemoryMap(self.env, self.io)
        self.interpreter = Interpreter(
            self.program, self.env, self.io, memory, self.debug, self.graphics
        )
        self.running = True
        self.file_dir = file_dir  # Répertoire de base pour SAVE/LOAD (SEC-BP-22)
        self._setup_graphics_render()

    def _setup_graphics_render(self) -> None:
        """Branche le rendu graphique temps réel sur le terminal (ADR-004)."""
        import sys
        import time

        self._last_render_time = 0.0
        _min_interval = 1.0 / 30  # 30 FPS max

        def _on_draw():
            now = time.monotonic()
            if now - self._last_render_time < _min_interval:
                return
            self._last_render_time = now
            gfx = self.graphics
            if gfx.mode == "lores":
                sys.stdout.write("\033[H")  # Curseur en haut
                sys.stdout.write(gfx.render_lores_ansi())
                sys.stdout.write("\n")
                sys.stdout.flush()
            elif gfx.mode == "hires":
                sys.stdout.write("\033[H")
                sys.stdout.write(gfx.render_hires_ansi())
                sys.stdout.write("\n")
                sys.stdout.flush()

        self.graphics.set_on_draw(_on_draw)

    def _render_final_frame(self) -> None:
        """Rendu final après fin de programme (force l'affichage de l'état courant)."""
        import sys

        gfx = self.graphics
        if gfx.mode == "lores":
            sys.stdout.write("\033[H")
            sys.stdout.write(gfx.render_lores_ansi())
            sys.stdout.write("\n")
            sys.stdout.flush()
        elif gfx.mode == "hires":
            sys.stdout.write("\033[H")
            sys.stdout.write(gfx.render_hires_ansi())
            sys.stdout.write("\n")
            sys.stdout.flush()

    def run(self) -> None:
        """Lance la boucle REPL."""
        while self.running:
            try:
                self.io.print_str("]")
                line = self.io.input_str()
                self._process_line(line)
            except EOFError:
                self.running = False
            except KeyboardInterrupt:
                self.io.print_str("\n")

    def _process_line(self, line: str) -> None:
        """Traite une ligne saisie par l'utilisateur."""
        if not line.strip():
            return

        # Commandes DEBUG ON / DEBUG OFF (hors tokenisation BASIC)
        upper = line.strip().upper()
        if upper == "DEBUG ON":
            self.debug.enable()
            self.io.print_str("DEBUG ON\n")
            return
        if upper == "DEBUG OFF":
            self.debug.disable()
            self.io.print_str("DEBUG OFF\n")
            return

        try:
            tokens = tokenize(line)
        except Exception:
            self.io.print_str("?SYNTAX ERROR\n")
            return

        if not tokens:
            return

        # Mode différé : la ligne commence par un numéro
        if tokens[0].type == TokenType.LINENUM:
            self._handle_deferred(tokens)
            return

        # Mode direct : exécution immédiate
        self._handle_direct(tokens)

    def _handle_deferred(self, tokens: list[Token]) -> None:
        """Gère le mode différé (stockage en mémoire)."""
        line_num = tokens[0].value

        # Validation du numéro de ligne
        if line_num > MAX_LINE_NUMBER:
            self.io.print_str("?SYNTAX ERROR\n")
            return

        # Numéro seul → suppression de la ligne
        if len(tokens) == 1:
            self.program.delete_line(line_num)
            self.env.mark_program_modified()
            return

        # Stocker les tokens (sans le numéro de ligne) dans le programme
        self.program.add_line(line_num, tokens[1:])
        self.env.mark_program_modified()

    def _handle_direct(self, tokens: list[Token]) -> None:
        """Gère le mode direct (exécution immédiate)."""
        try:
            stmt_list = parse_tokens(tokens)
        except BasicError as e:
            self.io.print_str(e.format() + "\n")
            return

        for stmt in stmt_list.statements:
            try:
                self._execute_direct(stmt)
            except BasicError as e:
                self.io.print_str(e.format() + "\n")
                return

    def _execute_direct(self, stmt: object) -> None:
        """Exécute une instruction en mode direct."""
        if isinstance(stmt, ast.ListStmt):
            self._cmd_list(stmt)
        elif isinstance(stmt, ast.NewStmt):
            self._cmd_new()
        elif isinstance(stmt, ast.DelStmt):
            self._cmd_del(stmt)
        elif isinstance(stmt, ast.RunStmt):
            self._cmd_run(stmt)
        elif isinstance(stmt, ast.ContStmt):
            self._cmd_cont()
        elif isinstance(stmt, ast.SaveStmt):
            self._cmd_save(stmt)
        elif isinstance(stmt, ast.LoadStmt):
            self._cmd_load(stmt)
        else:
            # Exécuter via l'Interpreter en mode direct
            self.interpreter.execute_direct(ast.StatementList([stmt]))

    def _cmd_list(self, stmt: ast.ListStmt) -> None:
        """Commande LIST : affiche le programme."""
        lines = self.program.get_lines_range(stmt.start, stmt.end)
        for line in lines:
            text = self.program.detokenize_line(line)
            self.io.print_str(text + "\n")

    def _cmd_new(self) -> None:
        """Commande NEW : efface le programme et les variables."""
        self.program.clear()
        self.env.reset()

    def _cmd_del(self, stmt: ast.DelStmt) -> None:
        """Commande DEL : supprime une plage de lignes."""
        self.program.delete_range(stmt.start, stmt.end)
        self.env.mark_program_modified()

    def _cmd_run(self, stmt: ast.RunStmt) -> None:
        """Commande RUN : exécute le programme."""
        try:
            self.interpreter.run(stmt.start_line)
        except BasicError as e:
            self.io.print_str(e.format() + "\n")
        finally:
            self._render_final_frame()

    def _cmd_cont(self) -> None:
        """Commande CONT : reprend l'exécution."""
        try:
            self.interpreter.continue_execution()
        except BasicError as e:
            self.io.print_str(e.format() + "\n")

    def _cmd_save(self, stmt: ast.SaveStmt) -> None:
        """Commande SAVE : sauvegarde le programme (UC-004)."""
        # Évaluer le nom de fichier en mode direct
        interp = self.interpreter
        filename = interp._eval(stmt.filename)
        if not isinstance(filename, str) or not filename:
            raise BasicError(16)  # SYNTAX ERROR
        # Ajout automatique de l'extension .bas si absente (CA-UC-004-01)
        if not filename.lower().endswith(".bas"):
            filename += ".bas"
        content = self.program.detokenize_all()
        self.io.save_file(filename, content + "\n", base_dir=self.file_dir)

    def _cmd_load(self, stmt: ast.LoadStmt) -> None:
        """Commande LOAD : charge un programme (UC-005)."""
        interp = self.interpreter
        filename = interp._eval(stmt.filename)
        if not isinstance(filename, str) or not filename:
            raise BasicError(16)  # SYNTAX ERROR
        # Ajout automatique de l'extension .bas si absente (CA-UC-005-01)
        if not filename.lower().endswith(".bas"):
            filename += ".bas"
        content = self.io.load_file(filename, base_dir=self.file_dir)
        # Remplacer le programme et réinitialiser
        self.program.clear()
        self.env.reset()
        for raw_line in content.splitlines():
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                tokens = tokenize(raw_line)
                if tokens and tokens[0].type == TokenType.LINENUM:
                    self.program.add_line(tokens[0].value, tokens[1:])
            except Exception:  # noqa: S110 — SEC-BP-23 : lignes non-parsables ignorées
                pass
