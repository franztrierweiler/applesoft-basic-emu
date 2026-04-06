"""Tests QA — Lot 02 : Interpréteur cœur (variables, expressions, affichage).

Scénarios du plan de test qa/plan-test/lot-02-interpreteur-coeur.md
"""

import ast as python_ast

import pytest

from applesoft.environment import Environment
from applesoft.errors import BasicError
from applesoft.interpreter import Interpreter
from applesoft.io_cli import IOBridgeCLI
from applesoft.lexer import TokenType, tokenize
from applesoft.parser import parse_tokens
from applesoft.program import Program
from applesoft.repl import REPL

# ── Helpers ──────────────────────────────────────────────────────────────


class MockIO(IOBridgeCLI):
    def __init__(self, inputs=None):
        super().__init__()
        self._inputs = inputs or []
        self._input_idx = 0
        self._output: list[str] = []

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

    @property
    def output(self) -> str:
        return "".join(self._output)


def run_program(lines: list[str], start_line=None) -> str:
    io = MockIO()
    prog = Program()
    env = Environment()
    for line in lines:
        tokens = tokenize(line)
        if tokens and tokens[0].type == TokenType.LINENUM:
            prog.add_line(tokens[0].value, tokens[1:])
    interp = Interpreter(prog, env, io)
    interp.run(start_line)
    return io.output


def run_direct(line: str) -> str:
    io = MockIO()
    prog = Program()
    env = Environment()
    interp = Interpreter(prog, env, io)
    tokens = tokenize(line)
    stmt_list = parse_tokens(tokens)
    interp.execute_direct(stmt_list)
    return io.output


def repl_session(inputs: list[str]) -> tuple[REPL, str]:
    io = MockIO(inputs)
    repl = REPL(io)
    repl.run()
    return repl, io.output


# ═══════════════════════════════════════════════════════════════════════
# T01 — UC-003 : Exécuter un programme
# ═══════════════════════════════════════════════════════════════════════


class TestT01UC003:
    def test_t01_01_sequential_run(self):
        """T01-01 [🔴] Exécution séquentielle → A puis B."""
        out = run_program(['10 PRINT "A"', '20 PRINT "B"'])
        assert out == "A\nB\n"

    def test_t01_02_run_from_line(self):
        """T01-02 [🔴] RUN 20 → seul B."""
        out = run_program(['10 PRINT "A"', '20 PRINT "B"'], start_line=20)
        assert out == "B\n"

    def test_t01_03_variable_print(self):
        """T01-03 [🔴] X=5 puis PRINT X → 5."""
        out = run_program(["10 X=5", "20 PRINT X"])
        assert " 5\n" in out

    def test_t01_04_end_stops(self):
        """T01-04 [🔴] END arrête l'exécution."""
        out = run_program(['10 PRINT "A" : END : PRINT "B"'])
        assert "A\n" in out
        assert "B" not in out

    def test_t01_05_stop_cont(self):
        """T01-05 [🔴] STOP + CONT → reprend après STOP."""
        io = MockIO()
        prog = Program()
        env = Environment()
        for line in ['10 PRINT "A"', "20 STOP", '30 PRINT "B"']:
            tokens = tokenize(line)
            prog.add_line(tokens[0].value, tokens[1:])
        interp = Interpreter(prog, env, io)
        interp.run()
        assert "A\n" in io.output
        assert "BREAK IN 20" in io.output
        io._output.clear()
        interp.continue_execution()
        assert "B\n" in io.output

    def test_t01_06_stop_modify_cont(self):
        """T01-06 [🔴] STOP + modif variable + CONT."""
        io = MockIO()
        prog = Program()
        env = Environment()
        for line in ["10 X=1", "20 STOP", "30 PRINT X"]:
            tokens = tokenize(line)
            prog.add_line(tokens[0].value, tokens[1:])
        interp = Interpreter(prog, env, io)
        interp.run()
        env.set_var("X", 99.0)
        io._output.clear()
        interp.continue_execution()
        assert " 99\n" in io.output

    def test_t01_07_run_empty(self):
        """T01-07 [🟠] RUN sans programme → pas d'erreur."""
        out = run_program([])
        assert out == ""

    def test_t01_08_run_undef_line(self):
        """T01-08 [🔴] RUN 99 (inexistante) → UNDEF'D STATEMENT."""
        with pytest.raises(BasicError) as exc:
            run_program(['10 PRINT "A"'], start_line=99)
        assert exc.value.code == 90

    def test_t01_09_cont_without_stop(self):
        """T01-09 [🔴] CONT sans arrêt → CAN'T CONTINUE."""
        io = MockIO()
        interp = Interpreter(Program(), Environment(), io)
        with pytest.raises(BasicError) as exc:
            interp.continue_execution()
        assert exc.value.code == 254

    def test_t01_10_cont_after_modify(self):
        """T01-10 [🟠] CONT après modif programme → CAN'T CONTINUE."""
        _, out = repl_session(["10 STOP", "RUN", '10 PRINT "X"', "CONT"])
        assert "CAN'T CONTINUE" in out

    def test_t01_11_implicit_end(self):
        """T01-11 [🟠] Fin sans END → terminaison implicite."""
        out = run_program(['10 PRINT "DONE"'])
        assert "DONE\n" in out


# ═══════════════════════════════════════════════════════════════════════
# T02 — UC-006 : Afficher des données
# ═══════════════════════════════════════════════════════════════════════


class TestT02UC006:
    def test_t02_01_print_string(self):
        """T02-01 [🔴] PRINT "HELLO" → HELLO + retour ligne."""
        assert run_direct('PRINT "HELLO"') == "HELLO\n"

    def test_t02_02_semicolon(self):
        """T02-02 [🔴] PRINT "A";"B" → AB."""
        assert run_direct('PRINT "A";"B"') == "AB\n"

    def test_t02_03_comma_tab(self):
        """T02-03 [🔴] PRINT "A","B" → A + tab 16 cols + B."""
        out = run_direct('PRINT "A","B"')
        # "A" en col 1, tab avance à col 17, donc 15 espaces entre A et B
        assert out.startswith("A")
        idx_b = out.index("B")
        assert idx_b >= 15

    def test_t02_04_trailing_semicolon(self):
        """T02-04 [🔴] PRINT "A"; + PRINT "B" → AB."""
        out = run_program(['10 PRINT "A";', '20 PRINT "B"'])
        assert out == "AB\n"

    def test_t02_05_print_empty(self):
        """T02-05 [🟠] PRINT seul → ligne vide."""
        assert run_direct("PRINT") == "\n"

    def test_t02_06_question_mark(self):
        """T02-06 [🟠] ? "HELLO" → HELLO."""
        assert run_direct('? "HELLO"') == "HELLO\n"

    def test_t02_07_spc(self):
        """T02-07 [🟠] PRINT SPC(5);"X" → 5 espaces + X."""
        assert run_direct('PRINT SPC(5);"X"') == "     X\n"

    def test_t02_08_tab(self):
        """T02-08 [🟠] PRINT TAB(10);"X" → X en colonne 10."""
        out = run_direct('PRINT TAB(10);"X"')
        assert out.index("X") == 9  # 0-based: col 10 = index 9

    def test_t02_09_tab_beyond(self):
        """T02-09 [🟠] TAB au-delà du curseur → nouvelle ligne."""
        out = run_program(['10 PRINT "ABCDEFGHIJ";TAB(5);"X"'])
        assert "\n" in out
        lines = out.split("\n")
        assert len(lines) >= 2

    def test_t02_10_pos(self):
        """T02-10 [🟠] POS(0) retourne la colonne courante."""
        out = run_program(['10 PRINT "ABC";', "20 PRINT POS(0)"])
        assert "4" in out

    def test_t02_11_division_by_zero(self):
        """T02-11 [🔴] PRINT 1/0 → DIVISION BY ZERO ERROR."""
        with pytest.raises(BasicError) as exc:
            run_direct("PRINT 1/0")
        assert exc.value.code == 133

    def test_t02_12_positive_space(self):
        """T02-12 [🔴] Nombre positif → espace avant."""
        out = run_direct("PRINT 42")
        assert out.startswith(" 42")

    def test_t02_13_negative_no_space(self):
        """T02-13 [🔴] Nombre négatif → pas d'espace."""
        out = run_direct("PRINT -5")
        assert out.startswith("-5")


# ═══════════════════════════════════════════════════════════════════════
# T03 — UC-010 : Variables
# ═══════════════════════════════════════════════════════════════════════


class TestT03UC010:
    def test_t03_01_let_explicit(self):
        """T03-01 [🔴] LET A = 5 : PRINT A → 5."""
        assert " 5\n" in run_direct("LET A = 5 : PRINT A")

    def test_t03_02_let_implicit(self):
        """T03-02 [🔴] A = 5 : PRINT A → 5."""
        assert " 5\n" in run_direct("A = 5 : PRINT A")

    def test_t03_03_uninitialized(self):
        """T03-03 [🔴] PRINT X → 0."""
        assert " 0\n" in run_direct("PRINT X")

    def test_t03_04_dim_array(self):
        """T03-04 [🔴] DIM A(5) / A(3)=42 → 42."""
        out = run_program(["10 DIM A(5)", "20 A(3)=42", "30 PRINT A(3)"])
        assert " 42\n" in out

    def test_t03_05_dim_2d(self):
        """T03-05 [🔴] DIM B(2,3) / B(1,2)=7 → 7."""
        out = run_program(["10 DIM B(2,3)", "20 B(1,2)=7", "30 PRINT B(1,2)"])
        assert " 7\n" in out

    def test_t03_06_auto_dim(self):
        """T03-06 [🔴] A(3)=5 sans DIM → auto-dim."""
        out = run_program(["10 A(3)=5", "20 PRINT A(3)"])
        assert " 5\n" in out

    def test_t03_07_bad_subscript(self):
        """T03-07 [🔴] A(11) sans DIM → BAD SUBSCRIPT."""
        with pytest.raises(BasicError) as exc:
            run_program(["10 A(11)=1"])
        assert exc.value.code == 107

    def test_t03_08_redim(self):
        """T03-08 [🟠] DIM A(5) deux fois → REDIM'D ARRAY."""
        with pytest.raises(BasicError) as exc:
            run_program(["10 DIM A(5)", "20 DIM A(10)"])
        assert exc.value.code == 120


# ═══════════════════════════════════════════════════════════════════════
# T04 — UC-011 : Expressions
# ═══════════════════════════════════════════════════════════════════════


class TestT04UC011:
    def test_t04_01_precedence(self):
        """T04-01 [🔴] 2+3*4 → 14."""
        assert " 14\n" in run_direct("PRINT 2+3*4")

    def test_t04_02_parens(self):
        """T04-02 [🔴] (2+3)*4 → 20."""
        assert " 20\n" in run_direct("PRINT (2+3)*4")

    def test_t04_03_power_right(self):
        """T04-03 [🔴] 2^3^2 → 512."""
        assert " 512\n" in run_direct("PRINT 2^3^2")

    def test_t04_04_sub_left(self):
        """T04-04 [🔴] 10-3-2 → 5."""
        assert " 5\n" in run_direct("PRINT 10-3-2")

    def test_t04_05_gt(self):
        """T04-05 [🔴] 5>3 → 1."""
        assert " 1\n" in run_direct("PRINT 5>3")

    def test_t04_06_eq(self):
        """T04-06 [🔴] 5=3 → 0."""
        assert " 0\n" in run_direct("PRINT 5=3")

    def test_t04_07_string_cmp(self):
        """T04-07 [🔴] "B">"A" → 1."""
        assert " 1\n" in run_direct('PRINT "B">"A"')

    def test_t04_08_and(self):
        """T04-08 [🔴] 1 AND 0 → 0."""
        assert " 0\n" in run_direct("PRINT 1 AND 0")

    def test_t04_09_or(self):
        """T04-09 [🔴] 1 OR 0 → 1."""
        assert " 1\n" in run_direct("PRINT 1 OR 0")

    def test_t04_10_not(self):
        """T04-10 [🔴] NOT 0 → 1."""
        assert " 1\n" in run_direct("PRINT NOT 0")

    def test_t04_11_compound(self):
        """T04-11 [🟠] 5>3 AND 2<4 → 1."""
        assert " 1\n" in run_direct("PRINT 5>3 AND 2<4")

    def test_t04_12_bitwise_and(self):
        """T04-12 [🟠] 12 AND 10 → 8."""
        assert " 8\n" in run_direct("PRINT 12 AND 10")

    def test_t04_13_zero_power_zero(self):
        """T04-13 [🟠] 0^0 → 1."""
        assert " 1\n" in run_direct("PRINT 0^0")

    def test_t04_14_unary_precedence(self):
        """T04-14 [🔴] -2^2 → 4 ((-2)^2)."""
        assert " 4\n" in run_direct("PRINT -2^2")

    def test_t04_15_equal_less(self):
        """T04-15 [🟠] 5 =< 5 → 1."""
        assert " 1\n" in run_direct("PRINT 5 =< 5")

    def test_t04_16_type_mismatch_cmp(self):
        """T04-16 [🔴] 5>"A" → TYPE MISMATCH."""
        with pytest.raises(BasicError) as exc:
            run_direct('PRINT 5>"A"')
        assert exc.value.code == 163


# ═══════════════════════════════════════════════════════════════════════
# T05 — RG-0006 : Types numériques
# ═══════════════════════════════════════════════════════════════════════


class TestT05RG0006:
    def test_t05_01_int_overflow(self):
        """T05-01 [🔴] X%=32768 → ILLEGAL QUANTITY."""
        with pytest.raises(BasicError) as exc:
            run_direct("X%=32768")
        assert exc.value.code == 53

    def test_t05_02_int_truncation(self):
        """T05-02 [🟠] X%=3.7 → tronqué à 3."""
        out = run_direct("X%=3.7 : PRINT X%")
        assert " 3\n" in out

    def test_t05_03_overflow(self):
        """T05-03 [🟠] EXP(1000) → OVERFLOW."""
        with pytest.raises(BasicError) as exc:
            run_direct("PRINT EXP(1000)")
        assert exc.value.code == 69


# ═══════════════════════════════════════════════════════════════════════
# T06 — RG-0007 : Chaînes
# ═══════════════════════════════════════════════════════════════════════


class TestT06RG0007:
    def test_t06_01_concat(self):
        """T06-01 [🔴] Concaténation A$+B$ → HELLO WORLD."""
        out = run_direct('A$="HELLO" : B$=" WORLD" : PRINT A$+B$')
        assert "HELLO WORLD\n" in out

    def test_t06_02_string_too_long(self):
        """T06-02 [🔴] Concaténation > 255 → STRING TOO LONG."""
        io = MockIO()
        prog = Program()
        env = Environment()
        env.set_var("A$", "X" * 200)
        env.set_var("B$", "Y" * 60)
        interp = Interpreter(prog, env, io)
        tokens = tokenize("PRINT A$+B$")
        with pytest.raises(BasicError) as exc:
            interp.execute_direct(parse_tokens(tokens))
        assert exc.value.code == 176

    def test_t06_03_type_mismatch_str(self):
        """T06-03 [🔴] A$=5 → TYPE MISMATCH."""
        with pytest.raises(BasicError) as exc:
            run_direct("A$=5")
        assert exc.value.code == 163

    def test_t06_04_type_mismatch_num(self):
        """T06-04 [🔴] A="TEXT" → TYPE MISMATCH."""
        with pytest.raises(BasicError) as exc:
            run_direct('A="TEXT"')
        assert exc.value.code == 163


# ═══════════════════════════════════════════════════════════════════════
# T07 — RG-0008/0009 : Multi-commandes et REM
# ═══════════════════════════════════════════════════════════════════════


class TestT07RG0008_0009:
    def test_t07_01_multi_stmt(self):
        """T07-01 [🔴] PRINT "A" : PRINT "B" → A puis B."""
        assert run_direct('PRINT "A" : PRINT "B"') == "A\nB\n"

    def test_t07_02_rem_ignored(self):
        """T07-02 [🔴] REM → ignoré."""
        out = run_program(["10 REM COMMENTAIRE", '20 PRINT "OK"'])
        assert "COMMENTAIRE" not in out
        assert "OK\n" in out

    def test_t07_03_rem_eats_colon(self):
        """T07-03 [🔴] REM : PRINT → rien."""
        out = run_program(['10 REM TEXTE : PRINT "CACHÉ"'])
        assert "CACHÉ" not in out


# ═══════════════════════════════════════════════════════════════════════
# T08 — Sécurité
# ═══════════════════════════════════════════════════════════════════════


class TestT08Security:
    def test_t08_01_no_eval_exec(self):
        """T08-01 [🔴] Pas d'eval/exec dans interpreter.py et environment.py."""
        for path in [
            "src/applesoft/interpreter.py",
            "src/applesoft/environment.py",
        ]:
            with open(path) as f:
                source = f.read()
            tree = python_ast.parse(source)
            for node in python_ast.walk(tree):
                if isinstance(node, python_ast.Call):
                    func = node.func
                    if isinstance(func, python_ast.Name):
                        assert func.id not in ("eval", "exec", "compile"), (
                            f"{path} contient un appel à {func.id}()"
                        )
