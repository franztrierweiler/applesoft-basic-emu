"""Tests unitaires pour DebugTracer.

Couvre activation/désactivation, sortie sur stderr,
et intégration avec l'interpréteur.
"""

import io as io_module
import sys

from applesoft.debug import DebugTracer
from applesoft.environment import Environment
from applesoft.interpreter import Interpreter
from applesoft.io_cli import IOBridgeCLI
from applesoft.lexer import tokenize
from applesoft.memory import MemoryMap
from applesoft.program import Program


class FakeIO(IOBridgeCLI):
    """IOBridge capturant la sortie."""

    def __init__(self):
        super().__init__()
        self.output = ""

    def print_str(self, text: str) -> None:
        self.output += text
        if "\n" in text:
            last_line = text.rsplit("\n", 1)[-1]
            self._cursor_column = len(last_line) + 1
        else:
            self._cursor_column += len(text)

    def clear_screen(self) -> None:
        self._cursor_column = 1


class TestDebugTracer:
    """Tests du DebugTracer."""

    def test_tracer_disabled_by_default(self):
        """Le tracer est désactivé par défaut."""
        tracer = DebugTracer()
        assert not tracer.enabled

    def test_enable_disable(self):
        """Activation et désactivation."""
        tracer = DebugTracer()
        tracer.enable()
        assert tracer.enabled
        tracer.disable()
        assert not tracer.enabled

    def test_trace_output_on_stderr(self):
        """La trace est écrite sur stderr."""
        tracer = DebugTracer()
        tracer.enable()
        captured = io_module.StringIO()
        old_stderr = sys.stderr
        sys.stderr = captured
        try:
            tracer.trace(10, "PRINT X")
        finally:
            sys.stderr = old_stderr
        output = captured.getvalue()
        assert "10" in output
        assert "PRINT X" in output

    def test_trace_silent_when_disabled(self):
        """Aucune sortie quand le tracer est désactivé."""
        tracer = DebugTracer()
        captured = io_module.StringIO()
        old_stderr = sys.stderr
        sys.stderr = captured
        try:
            tracer.trace(10, "PRINT X")
        finally:
            sys.stderr = old_stderr
        assert captured.getvalue() == ""

    def test_trace_with_variables(self):
        """La trace peut inclure l'état des variables."""
        tracer = DebugTracer()
        tracer.enable()
        captured = io_module.StringIO()
        old_stderr = sys.stderr
        sys.stderr = captured
        try:
            tracer.trace(10, "PRINT X", {"X": 42})
        finally:
            sys.stderr = old_stderr
        output = captured.getvalue()
        assert "X" in output
        assert "42" in output


class TestDebugIntegration:
    """Tests intégration du DebugTracer avec l'interpréteur."""

    def test_interpreter_traces_when_debug_enabled(self):
        """L'interpréteur trace les instructions quand le debug est activé."""
        io = FakeIO()
        program = Program()
        env = Environment()
        memory = MemoryMap(env, io)
        tracer = DebugTracer()
        tracer.enable()
        interp = Interpreter(program, env, io, memory, tracer)

        tokens = tokenize('PRINT "HELLO"')
        program.add_line(10, tokens)

        captured = io_module.StringIO()
        old_stderr = sys.stderr
        sys.stderr = captured
        try:
            interp.run()
        finally:
            sys.stderr = old_stderr

        # La sortie BASIC va sur stdout (capturée par FakeIO)
        assert "HELLO" in io.output
        # La trace va sur stderr
        assert "10" in captured.getvalue()

    def test_interpreter_no_trace_when_debug_disabled(self):
        """Pas de trace quand le debug est désactivé."""
        io = FakeIO()
        program = Program()
        env = Environment()
        memory = MemoryMap(env, io)
        tracer = DebugTracer()  # Désactivé par défaut
        interp = Interpreter(program, env, io, memory, tracer)

        tokens = tokenize('PRINT "HELLO"')
        program.add_line(10, tokens)

        captured = io_module.StringIO()
        old_stderr = sys.stderr
        sys.stderr = captured
        try:
            interp.run()
        finally:
            sys.stderr = old_stderr

        assert "HELLO" in io.output
        assert captured.getvalue() == ""
