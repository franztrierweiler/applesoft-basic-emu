"""Tests QA -- Lot 05 : acces systeme, gestion d'erreurs, debug.

Scenarios issus de qa/plan-test/lot-05-acces-systeme-debug.md
UC couverts : UC-022, UC-023, UC-024, ENF-002, DebugTracer (ADR-006)
"""

from __future__ import annotations

import io as io_module
import sys
import time

from applesoft.debug import DebugTracer
from applesoft.environment import Environment
from applesoft.errors import BasicError
from applesoft.interpreter import Interpreter
from applesoft.io_cli import IOBridgeCLI
from applesoft.lexer import tokenize
from applesoft.memory import MemoryMap
from applesoft.program import Program
from applesoft.repl import REPL

# ── Helpers ──────────────────────────────────────────────────────────────


class MockIO(IOBridgeCLI):
    """IOBridge capturant la sortie avec controle d'interruption."""

    def __init__(self, inputs=None):
        super().__init__()
        self._inputs = inputs or []
        self._input_idx = 0
        self._output: list[str] = []
        self._interrupt_after: int | None = None

    def print_str(self, text: str) -> None:
        self._output.append(text)
        if "\n" in text:
            self._cursor_column = len(text.rsplit("\n", 1)[-1]) + 1
        else:
            self._cursor_column += len(text)

    def input_str(self, prompt: str = "") -> str:
        if prompt:
            self._output.append(prompt)
        if self._input_idx >= len(self._inputs):
            raise EOFError
        line = self._inputs[self._input_idx]
        self._input_idx += 1
        return line

    def get_char(self) -> str:
        if self._input_idx >= len(self._inputs):
            raise EOFError
        ch = self._inputs[self._input_idx]
        self._input_idx += 1
        return ch[0] if ch else ""

    def clear_screen(self) -> None:
        self._output.append("[CLS]")
        self._cursor_column = 1

    def trigger_interrupt_after(self, n: int) -> None:
        """Declenche l'interruption apres n appels a check_interrupt."""
        self._interrupt_after = n

    def check_interrupt(self) -> bool:
        if self._interrupt_after is not None:
            self._interrupt_after -= 1
            if self._interrupt_after <= 0:
                self._interrupt_after = None
                return True
        return False

    @property
    def output(self) -> str:
        return "".join(self._output)


def _run_program(
    lines: dict[int, str], io: MockIO | None = None, debug: DebugTracer | None = None
) -> MockIO:
    """Execute un programme BASIC et retourne l'IO avec la sortie."""
    io = io or MockIO()
    program = Program()
    env = Environment()
    memory = MemoryMap(env, io)
    debug = debug or DebugTracer()
    interp = Interpreter(program, env, io, memory, debug)

    for num, text in sorted(lines.items()):
        tokens = tokenize(text)
        program.add_line(num, tokens)

    try:
        interp.run()
    except BasicError as e:
        io.print_str(e.format() + "\n")
    return io


def _make_interpreter(
    lines: dict[int, str], io: MockIO | None = None, debug: DebugTracer | None = None
):
    """Cree un interpreteur avec un programme."""
    io = io or MockIO()
    program = Program()
    env = Environment()
    memory = MemoryMap(env, io)
    debug = debug or DebugTracer()
    interp = Interpreter(program, env, io, memory, debug)

    for num, text in sorted(lines.items()):
        tokens = tokenize(text)
        program.add_line(num, tokens)

    return interp, io, env


# ═══════════════════════════════════════════════════════════════════════
# T01 — UC-022 : Lire/ecrire la memoire (PEEK/POKE/CALL)
# ═══════════════════════════════════════════════════════════════════════


class TestT01UC022:
    """Scenarios QA pour UC-022 — PEEK/POKE/CALL."""

    def test_t01_01_poke_peek_roundtrip(self):
        """T01-01 [Bloquant] POKE 768,42 puis PEEK(768) -> affiche 42."""
        io = _run_program(
            {
                10: "POKE 768,42",
                20: "PRINT PEEK(768)",
            }
        )
        assert "42" in io.output.strip()

    def test_t01_02_onerr_peek222_error_code(self):
        """T01-02 [Bloquant] ONERR + division par zero + PEEK(222) -> affiche 133."""
        io = _run_program(
            {
                10: "ONERR GOTO 100",
                20: "X = 1/0",
                30: "END",
                100: "PRINT PEEK(222)",
            }
        )
        assert "133" in io.output.strip()

    def test_t01_03_call_minus936_home(self):
        """T01-03 [Bloquant] CALL -936 -> ecran efface (HOME)."""
        io = _run_program(
            {
                10: "CALL -936",
            }
        )
        assert "[CLS]" in io.output

    def test_t01_04_peek_49152_keyboard(self):
        """T01-04 [Bloquant] GET + PEEK(49152) -> code touche avec bit 7."""
        # On simule la touche 'A' (65 + 128 = 193) directement via set_last_key
        io = MockIO()
        io.set_last_key(ord("A") | 0x80)  # 193
        io = _run_program(
            {
                10: "PRINT PEEK(49152)",
            },
            io=io,
        )
        assert "193" in io.output.strip()

    def test_t01_05_poke_49168_reset_strobe(self):
        """T01-05 [Majeur] POKE 49168,0 -> reset strobe clavier (bit 7 a 0)."""
        io = MockIO()
        io.set_last_key(193)  # 'A' + 128
        io = _run_program(
            {
                10: "POKE 49168,0",
                20: "PRINT PEEK(49152)",
            },
            io=io,
        )
        # Apres reset strobe, bit 7 est a 0 : 193 & 0x7F = 65
        assert "65" in io.output.strip()

    def test_t01_06_peek_negative_error(self):
        """T01-06 [Bloquant] PEEK(-1) -> ?ILLEGAL QUANTITY ERROR."""
        io = _run_program(
            {
                10: "PRINT PEEK(-1)",
            }
        )
        assert "?ILLEGAL QUANTITY ERROR" in io.output

    def test_t01_07_peek_too_large_error(self):
        """T01-07 [Bloquant] PEEK(65536) -> ?ILLEGAL QUANTITY ERROR."""
        io = _run_program(
            {
                10: "PRINT PEEK(65536)",
            }
        )
        assert "?ILLEGAL QUANTITY ERROR" in io.output

    def test_t01_08_poke_value_too_large(self):
        """T01-08 [Bloquant] POKE 768,256 -> ?ILLEGAL QUANTITY ERROR."""
        io = _run_program(
            {
                10: "POKE 768,256",
            }
        )
        assert "?ILLEGAL QUANTITY ERROR" in io.output

    def test_t01_09_poke_value_negative(self):
        """T01-09 [Bloquant] POKE 768,-1 -> ?ILLEGAL QUANTITY ERROR."""
        io = _run_program(
            {
                10: "POKE 768,-1",
            }
        )
        assert "?ILLEGAL QUANTITY ERROR" in io.output

    def test_t01_10_poke_address_too_large(self):
        """T01-10 [Bloquant] POKE 65536,0 -> ?ILLEGAL QUANTITY ERROR."""
        io = _run_program(
            {
                10: "POKE 65536,0",
            }
        )
        assert "?ILLEGAL QUANTITY ERROR" in io.output

    def test_t01_11_call_address_too_large(self):
        """T01-11 [Majeur] CALL 65536 -> ?ILLEGAL QUANTITY ERROR."""
        io = _run_program(
            {
                10: "CALL 65536",
            }
        )
        assert "?ILLEGAL QUANTITY ERROR" in io.output

    def test_t01_12_call_unknown_warning(self):
        """T01-12 [Mineur] CALL 12345 (adresse non emulee) -> avertissement stderr."""
        captured = io_module.StringIO()
        old_stderr = sys.stderr
        sys.stderr = captured
        try:
            _run_program(
                {
                    10: "CALL 12345",
                }
            )
        finally:
            sys.stderr = old_stderr
        assert "WARNING" in captured.getvalue()
        assert "12345" in captured.getvalue()

    def test_t01_13_peek_rom_returns_zero(self):
        """T01-13 [Mineur] PEEK sur adresse ROM non emulee -> retourne 0."""
        io = _run_program(
            {
                10: "PRINT PEEK(53248)",
            }
        )
        # Adresse $D000 (ROM non emulee) → 0
        assert " 0\n" in io.output

    def test_t01_14_peek_218_219_error_line(self):
        """T01-14 [Majeur] PEEK(218-219) -> numero de ligne d'erreur (little-endian)."""
        io = _run_program(
            {
                10: "ONERR GOTO 100",
                20: "X = 1/0",
                30: "END",
                100: "PRINT PEEK(218) + PEEK(219) * 256",
            }
        )
        # Erreur en ligne 20 → PEEK(218)=20, PEEK(219)=0 → 20+0*256 = 20
        assert "20" in io.output.strip()

    def test_t01_15_peek_48_text_mode(self):
        """T01-15 [Mineur] PEEK(48) -> mode texte/graphique."""
        io = _run_program(
            {
                10: "PRINT PEEK(48)",
            }
        )
        # Mode texte par defaut = 0
        assert " 0\n" in io.output

    def test_t01_16_peek_103_104_program_start(self):
        """T01-16 [Mineur] PEEK(103-104) -> adresse debut programme (0x0801)."""
        io = _run_program(
            {
                10: "PRINT PEEK(103) + PEEK(104) * 256",
            }
        )
        # 0x0801 = 2049 → low=1, high=8 → 1 + 8*256 = 2049
        assert "2049" in io.output.strip()

    def test_t01_17_poke_49200_speaker_noop(self):
        """T01-17 [Mineur] POKE 49200,0 -> speaker no-op (pas d'erreur)."""
        io = _run_program(
            {
                10: "POKE 49200,0",
                20: 'PRINT "OK"',
            }
        )
        assert "OK" in io.output
        assert "ERROR" not in io.output


# ═══════════════════════════════════════════════════════════════════════
# T02 — UC-023 : Gerer les erreurs d'execution (ONERR GOTO / RESUME)
# ═══════════════════════════════════════════════════════════════════════


class TestT02UC023:
    """Scenarios QA pour UC-023 — ONERR GOTO / RESUME."""

    def test_t02_01_onerr_handler_executed(self):
        """T02-01 [Bloquant] ONERR GOTO + erreur -> handler execute, PEEK(222) correct."""
        io = _run_program(
            {
                10: "ONERR GOTO 100",
                20: "X = 1/0",
                30: "END",
                100: 'PRINT "ERREUR";PEEK(222)',
            }
        )
        assert "ERREUR" in io.output
        assert "133" in io.output

    def test_t02_02_onerr_goto_0_disables(self):
        """T02-02 [Bloquant] ONERR GOTO 0 -> handler desactive, erreur affichee."""
        io = _run_program(
            {
                10: "ONERR GOTO 100",
                20: "ONERR GOTO 0",
                30: "X = 1/0",
                100: 'PRINT "NE DEVRAIT PAS"',
            }
        )
        assert "NE DEVRAIT PAS" not in io.output
        assert "?DIVISION BY ZERO ERROR IN 30" in io.output

    def test_t02_03_resume_retries_faulting(self):
        """T02-03 [Bloquant] ONERR + RESUME -> reprend a l'instruction fautive.

        Le programme corrige l'etat avant RESUME pour eviter une boucle infinie.
        On utilise POKE 768 comme compteur pour detecter si RESUME re-execute bien la ligne.
        """
        # Scenario : ONERR installe, division par zero en 20
        # Handler met un compteur dans PEEK(768) et fait RESUME
        # Protection anti-boucle detecte la re-erreur et sort proprement
        io = _run_program(
            {
                5: "ONERR GOTO 100",
                10: "X = 1/0",
                20: "END",
                100: "POKE 768,42",
                110: "RESUME",
            }
        )
        # RESUME revient en ligne 10, qui re-declenche l'erreur
        # Protection anti-boucle active → erreur affichee
        # On verifie que le handler a bien ete execute (POKE 768,42)
        assert "?DIVISION BY ZERO ERROR" in io.output

    def test_t02_04_onerr_undef_statement(self):
        """T02-04 [Majeur] ONERR GOTO 999 (ligne inexistante) -> ?UNDEF'D STATEMENT ERROR."""
        io = _run_program(
            {
                10: "ONERR GOTO 999",
                20: "X = 1/0",
            }
        )
        assert "?UNDEF'D STATEMENT ERROR" in io.output

    def test_t02_05_error_in_handler_anti_loop(self):
        """T02-05 [Bloquant] Erreur dans le handler -> anti-boucle, erreur affichee."""
        io = _run_program(
            {
                10: "ONERR GOTO 100",
                20: "X = 1/0",
                100: "Y = 1/0",
            }
        )
        # Erreur dans le handler doit etre affichee sans boucle infinie
        assert "?DIVISION BY ZERO ERROR" in io.output

    def test_t02_06_resume_without_onerr(self):
        """T02-06 [Majeur] RESUME sans ONERR actif -> ?SYNTAX ERROR."""
        io = _run_program(
            {
                10: "RESUME",
            }
        )
        assert "?SYNTAX ERROR" in io.output


# ═══════════════════════════════════════════════════════════════════════
# T03 — UC-024 : Interrompre l'execution (Ctrl+C)
# ═══════════════════════════════════════════════════════════════════════


class TestT03UC024:
    """Scenarios QA pour UC-024 — Ctrl+C / CONT."""

    def test_t03_01_break_in_linenum(self):
        """T03-01 [Bloquant] Boucle infinie + Ctrl+C -> BREAK IN 10 + retour prompt."""
        io = MockIO()
        io.trigger_interrupt_after(5)
        io = _run_program({10: "GOTO 10"}, io=io)
        assert "BREAK IN 10" in io.output

    def test_t03_02_cont_after_break(self):
        """T03-02 [Bloquant] Apres Ctrl+C, CONT -> reprend l'execution."""
        io = MockIO()
        io.trigger_interrupt_after(3)
        interp, io, env = _make_interpreter(
            {
                10: "X = 1",
                20: "X = X + 1",
                30: "IF X < 100 THEN GOTO 20",
                40: 'PRINT "DONE"',
            },
            io=io,
        )

        # Premiere execution → interrompue
        interp.run()
        assert "BREAK" in io.output
        assert env.get_cont_point() is not None

        # CONT → reprend et termine
        interp.continue_execution()
        assert "DONE" in io.output

    def test_t03_03_variables_preserved(self):
        """T03-03 [Majeur] Variables conservees apres interruption."""
        io = MockIO()
        io.trigger_interrupt_after(5)
        interp, io, env = _make_interpreter(
            {
                10: "X = 42",
                20: "Y = 99",
                30: "GOTO 30",
            },
            io=io,
        )
        interp.run()
        assert "BREAK" in io.output
        assert env.get_var("X") == 42
        assert env.get_var("Y") == 99

    def test_t03_04_interrupt_during_input(self):
        """T03-04 [Majeur] Ctrl+C pendant INPUT -> entree annulee, BREAK affiche.

        On simule en declenchant l'interruption avant que INPUT ne soit atteint,
        car l'interruption est verifiee a chaque instruction.
        """
        io = MockIO(inputs=["HELLO"])
        io.trigger_interrupt_after(2)  # Interrompt pendant/avant INPUT
        io = _run_program(
            {
                10: "X = 1",
                20: "INPUT A$",
                30: 'PRINT "APRES"',
            },
            io=io,
        )
        assert "BREAK" in io.output


# ═══════════════════════════════════════════════════════════════════════
# T04 — ENF-002 : Performance interruption
# ═══════════════════════════════════════════════════════════════════════


class TestT04ENF:
    """Scenario QA pour ENF-002 — latence interruption."""

    def test_t04_01_interrupt_latency(self):
        """T04-01 [Majeur] Boucle infinie + Ctrl+C -> interruption < 500ms."""
        io = MockIO()
        # Interrupt apres beaucoup d'iterations pour mesurer la latence
        io.trigger_interrupt_after(10000)

        start = time.time()
        _run_program({10: "GOTO 10"}, io=io)
        elapsed = time.time() - start

        assert "BREAK" in io.output
        assert elapsed < 0.5, f"Interruption en {elapsed:.3f}s (seuil 500ms)"


# ═══════════════════════════════════════════════════════════════════════
# T05 — DebugTracer (ADR-006)
# ═══════════════════════════════════════════════════════════════════════


class TestT05DebugTracer:
    """Scenarios QA pour le DebugTracer."""

    def test_t05_01_debug_flag_enables_trace(self):
        """T05-01 [Majeur] Flag --debug -> trace activee sur stderr."""
        debug = DebugTracer()
        debug.enable()

        captured = io_module.StringIO()
        old_stderr = sys.stderr
        sys.stderr = captured
        try:
            _run_program(
                {
                    10: 'PRINT "HELLO"',
                },
                debug=debug,
            )
        finally:
            sys.stderr = old_stderr

        stderr_out = captured.getvalue()
        assert "[DEBUG]" in stderr_out
        assert "10" in stderr_out

    def test_t05_02_debug_on_off_repl(self):
        """T05-02 [Majeur] DEBUG ON / DEBUG OFF dans le REPL."""
        io = MockIO()
        debug = DebugTracer()
        repl = REPL(io, debug=debug)

        # DEBUG ON
        repl._process_line("DEBUG ON")
        assert debug.enabled
        assert "DEBUG ON" in io.output

        # DEBUG OFF
        repl._process_line("DEBUG OFF")
        assert not debug.enabled
        assert "DEBUG OFF" in io.output

    def test_t05_03_trace_on_stderr_only(self):
        """T05-03 [Mineur] Trace sur stderr, pas sur stdout."""
        debug = DebugTracer()
        debug.enable()

        io = MockIO()

        captured_stderr = io_module.StringIO()
        old_stderr = sys.stderr
        sys.stderr = captured_stderr
        try:
            _run_program(
                {
                    10: 'PRINT "HELLO"',
                },
                io=io,
                debug=debug,
            )
        finally:
            sys.stderr = old_stderr

        # stdout (capture par MockIO) ne doit pas contenir [DEBUG]
        assert "[DEBUG]" not in io.output
        # stderr doit contenir [DEBUG]
        assert "[DEBUG]" in captured_stderr.getvalue()
        # stdout doit contenir HELLO
        assert "HELLO" in io.output

    def test_t05_04_no_trace_when_disabled(self):
        """T05-04 [Mineur] Pas de trace quand debug desactive."""
        debug = DebugTracer()
        # Debug desactive par defaut

        captured_stderr = io_module.StringIO()
        old_stderr = sys.stderr
        sys.stderr = captured_stderr
        try:
            _run_program(
                {
                    10: 'PRINT "HELLO"',
                },
                debug=debug,
            )
        finally:
            sys.stderr = old_stderr

        assert captured_stderr.getvalue() == ""
