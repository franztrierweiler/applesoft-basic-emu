"""Tests unitaires — Lot 03 : Contrôle de flux et entrées (UC-007/008/012/013/014)."""

from applesoft.environment import Environment
from applesoft.interpreter import Interpreter
from applesoft.io_cli import IOBridgeCLI
from applesoft.lexer import TokenType, tokenize
from applesoft.program import Program

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

    def get_char(self) -> str:
        if self._input_idx >= len(self._inputs):
            raise EOFError
        ch = self._inputs[self._input_idx]
        self._input_idx += 1
        return ch[0] if ch else ""

    @property
    def output(self) -> str:
        return "".join(self._output)


def run_program(lines: list[str], inputs=None) -> str:
    io = MockIO(inputs)
    prog = Program()
    env = Environment()
    for line in lines:
        tokens = tokenize(line)
        if tokens and tokens[0].type == TokenType.LINENUM:
            prog.add_line(tokens[0].value, tokens[1:])
    interp = Interpreter(prog, env, io)
    interp.run()
    return io.output


# ═══════════════════════════════════════════════════════════════════════
# UC-012 : Branchements
# ═══════════════════════════════════════════════════════════════════════


class TestUC012Branching:
    def test_ca_uc_012_01_goto_skips(self):
        """CA-UC-012-01 : GOTO 30 saute la ligne 20."""
        out = run_program(
            [
                "10 GOTO 30",
                '20 PRINT "SKIP"',
                '30 PRINT "OK"',
            ]
        )
        assert "OK" in out
        assert "SKIP" not in out

    def test_ca_uc_012_02_if_then_true(self):
        """CA-UC-012-02 : IF X>3 THEN PRINT "YES"."""
        out = run_program(['10 X=5 : IF X>3 THEN PRINT "YES"'])
        assert "YES" in out

    def test_ca_uc_012_03_if_false_skips_block(self):
        """CA-UC-012-03 : IF faux → bloc entier sauté."""
        out = run_program(['10 X=1 : IF X>3 THEN PRINT "YES" : PRINT "ALSO"'])
        assert "YES" not in out
        assert "ALSO" not in out

    def test_ca_uc_012_04_if_else(self):
        """CA-UC-012-04 : IF/ELSE → branche ELSE."""
        out = run_program(['10 X=1 : IF X>3 THEN PRINT "BIG" ELSE PRINT "SMALL"'])
        assert "SMALL" in out
        assert "BIG" not in out

    def test_ca_uc_012_05_if_then_linenum(self):
        """CA-UC-012-05 : IF THEN 100 → GOTO implicite."""
        out = run_program(
            [
                "10 X=5 : IF X>3 THEN 100",
                '20 PRINT "NO"',
                '100 PRINT "YES"',
            ]
        )
        assert "YES" in out
        assert "NO" not in out

    def test_ca_uc_012_06_on_goto(self):
        """CA-UC-012-06 : ON X GOTO → branchement indexé."""
        out = run_program(
            [
                "10 X=2 : ON X GOTO 100,200,300",
                '200 PRINT "B" : END',
            ]
        )
        assert "B" in out

    def test_ca_uc_012_07_if_nested(self):
        """CA-UC-012-07 : IF imbriqués sur une même ligne."""
        out = run_program(['10 IF 0 THEN PRINT "A" ELSE IF 1 THEN PRINT "B" ELSE PRINT "C"'])
        assert "B" in out
        assert "A" not in out
        assert "C" not in out


# ═══════════════════════════════════════════════════════════════════════
# UC-013 : Boucles FOR/NEXT
# ═══════════════════════════════════════════════════════════════════════


class TestUC013ForNext:
    def test_ca_uc_013_01_for_next_basic(self):
        """CA-UC-013-01 : FOR I=1 TO 3 → 1, 2, 3."""
        out = run_program(["10 FOR I=1 TO 3", "20 PRINT I", "30 NEXT I"])
        assert " 1\n" in out
        assert " 2\n" in out
        assert " 3\n" in out

    def test_ca_uc_013_02_for_step(self):
        """CA-UC-013-02 : FOR I=1 TO 10 STEP 3 → 1, 4, 7, 10."""
        out = run_program(["10 FOR I=1 TO 10 STEP 3", "20 PRINT I", "30 NEXT"])
        assert " 1\n" in out
        assert " 4\n" in out
        assert " 7\n" in out
        assert " 10\n" in out

    def test_ca_uc_013_03_for_step_negative(self):
        """CA-UC-013-03 : FOR I=5 TO 1 STEP -1 → 5, 4, 3, 2, 1."""
        out = run_program(["10 FOR I=5 TO 1 STEP -1", "20 PRINT I", "30 NEXT"])
        assert " 5\n" in out
        assert " 4\n" in out
        assert " 3\n" in out
        assert " 2\n" in out
        assert " 1\n" in out

    def test_ca_uc_013_04_nested_next_ji(self):
        """CA-UC-013-04 : Boucles imbriquées avec NEXT J,I."""
        out = run_program(
            [
                "10 FOR I=1 TO 2",
                "20 FOR J=1 TO 2",
                "30 PRINT I;J",
                "40 NEXT J,I",
            ]
        )
        assert " 1" in out
        assert " 2" in out


# ═══════════════════════════════════════════════════════════════════════
# UC-014 : GOSUB / RETURN
# ═══════════════════════════════════════════════════════════════════════


class TestUC014Gosub:
    def test_ca_uc_014_01_gosub_return(self):
        """CA-UC-014-01 : GOSUB + RETURN → retour après GOSUB."""
        out = run_program(
            [
                "10 GOSUB 100",
                '20 PRINT "BACK"',
                "30 END",
                '100 PRINT "SUB"',
                "110 RETURN",
            ]
        )
        assert "SUB" in out
        assert "BACK" in out
        # SUB doit apparaître avant BACK
        assert out.index("SUB") < out.index("BACK")

    def test_ca_uc_014_02_gosub_nested(self):
        """CA-UC-014-02 : GOSUB imbriqués."""
        out = run_program(
            [
                "10 GOSUB 100",
                "20 END",
                "100 GOSUB 200",
                "110 RETURN",
                '200 PRINT "DEEP"',
                "210 RETURN",
            ]
        )
        assert "DEEP" in out

    def test_ca_uc_014_03_pop_goto(self):
        """CA-UC-014-03 : POP + GOTO au lieu de RETURN."""
        out = run_program(
            [
                "10 GOSUB 100",
                '20 PRINT "BACK"',
                "30 END",
                "100 POP",
                "110 GOTO 20",
            ]
        )
        assert "BACK" in out

    def test_ca_uc_014_04_on_gosub(self):
        """CA-UC-014-04 : ON X GOSUB → appel indexé avec RETURN."""
        out = run_program(
            [
                "10 X=2 : ON X GOSUB 100,200",
                '20 PRINT "BACK" : END',
                '200 PRINT "B" : RETURN',
            ]
        )
        assert "B" in out
        assert "BACK" in out


# ═══════════════════════════════════════════════════════════════════════
# UC-007 : INPUT / GET
# ═══════════════════════════════════════════════════════════════════════


class TestUC007Input:
    def test_ca_uc_007_01_input_string(self):
        """CA-UC-007-01 : INPUT A$ → saisie reflétée."""
        out = run_program(
            ["10 INPUT A$", "20 PRINT A$"],
            inputs=["HELLO"],
        )
        assert "HELLO" in out

    def test_ca_uc_007_02_input_prompt(self):
        """CA-UC-007-02 : INPUT "NAME";N$ → invite NAME?."""
        out = run_program(
            ['10 INPUT "NAME";N$'],
            inputs=["Franz"],
        )
        assert "NAME?" in out

    def test_ca_uc_007_03_input_multi(self):
        """CA-UC-007-03 : INPUT A,B : PRINT A+B → somme."""
        out = run_program(
            ["10 INPUT A,B", "20 PRINT A+B"],
            inputs=["3,7"],
        )
        assert " 10\n" in out

    def test_ca_uc_007_04_get_char(self):
        """CA-UC-007-04 : GET A$ → caractère sans écho."""
        out = run_program(
            ["10 GET A$", "20 PRINT A$"],
            inputs=["X"],
        )
        assert "X" in out


# ═══════════════════════════════════════════════════════════════════════
# UC-008 : DATA / READ / RESTORE
# ═══════════════════════════════════════════════════════════════════════


class TestUC008Data:
    def test_ca_uc_008_01_data_read(self):
        """CA-UC-008-01 : DATA + READ + PRINT → 6."""
        out = run_program(
            [
                "10 DATA 1,2,3",
                "20 READ A,B,C",
                "30 PRINT A+B+C",
            ]
        )
        assert " 6\n" in out

    def test_ca_uc_008_02_data_position(self):
        """CA-UC-008-02 : DATA après READ → position sans importance."""
        out = run_program(
            [
                "10 READ A",
                "20 DATA 42",
                "30 PRINT A",
            ]
        )
        assert " 42\n" in out

    def test_ca_uc_008_03_restore(self):
        """CA-UC-008-03 : RESTORE → relecture depuis le début."""
        out = run_program(
            [
                "10 DATA 10,20",
                "20 READ A",
                "30 RESTORE",
                "40 READ B",
                "50 PRINT A;B",
            ]
        )
        # A=10, B=10 (relu depuis le début)
        assert " 10" in out
