"""Tests unitaires pour l'interruption Ctrl+C (UC-024).

Couvre BREAK IN linenum, flag d'interruption, et CONT après interruption.
"""

from applesoft.environment import Environment
from applesoft.interpreter import Interpreter
from applesoft.io_cli import IOBridgeCLI
from applesoft.lexer import tokenize
from applesoft.memory import MemoryMap
from applesoft.program import Program


class FakeIO(IOBridgeCLI):
    """IOBridge avec contrôle du flag d'interruption pour les tests."""

    def __init__(self):
        super().__init__()
        self.output = ""
        self._interrupt_after = None  # Nombre d'instructions avant interruption

    def print_str(self, text: str) -> None:
        self.output += text
        if "\n" in text:
            last_line = text.rsplit("\n", 1)[-1]
            self._cursor_column = len(last_line) + 1
        else:
            self._cursor_column += len(text)

    def clear_screen(self) -> None:
        self._cursor_column = 1

    def trigger_interrupt_after(self, n: int) -> None:
        """Déclenche l'interruption après n appels à check_interrupt."""
        self._interrupt_after = n

    def check_interrupt(self) -> bool:
        if self._interrupt_after is not None:
            self._interrupt_after -= 1
            if self._interrupt_after <= 0:
                self._interrupt_after = None
                return True
        return False


def _make_interpreter(lines: dict[int, str], io: FakeIO | None = None):
    """Crée un interpréteur avec un programme."""
    io = io or FakeIO()
    program = Program()
    env = Environment()
    memory = MemoryMap(env, io)
    interp = Interpreter(program, env, io, memory)

    for num, text in sorted(lines.items()):
        tokens = tokenize(text)
        program.add_line(num, tokens)

    return interp, io, env


class TestCtrlCInterrupt:
    """Tests interruption Ctrl+C."""

    def test_ca_uc_024_01_break_in_linenum(self):
        """CA-UC-024-01 : Boucle infinie + Ctrl+C → BREAK IN 10."""
        io = FakeIO()
        io.trigger_interrupt_after(5)  # Interrompre après 5 vérifications
        interp, io, env = _make_interpreter({10: "GOTO 10"}, io)
        interp.run()
        assert "BREAK IN 10" in io.output

    def test_ca_uc_024_02_cont_after_break(self):
        """CA-UC-024-02 : Après Ctrl+C, CONT → reprend l'exécution."""
        io = FakeIO()
        # D'abord interrompre après quelques instructions
        io.trigger_interrupt_after(3)
        interp, io, env = _make_interpreter(
            {
                10: "X = 1",
                20: "X = X + 1",
                30: "GOTO 20",
            },
            io,
        )
        interp.run()
        assert "BREAK" in io.output
        # CONT doit pouvoir reprendre
        assert env.get_cont_point() is not None

    def test_interrupt_preserves_variables(self):
        """Après Ctrl+C, les variables sont conservées."""
        io = FakeIO()
        io.trigger_interrupt_after(5)
        interp, io, env = _make_interpreter(
            {
                10: "X = 42",
                20: "GOTO 20",
            },
            io,
        )
        interp.run()
        assert env.get_var("X") == 42

    def test_interrupt_flag_reset_after_check(self):
        """Le flag d'interruption est réinitialisé après vérification."""
        io = IOBridgeCLI()
        io.set_interrupted()
        assert io.check_interrupt() is True
        assert io.check_interrupt() is False
