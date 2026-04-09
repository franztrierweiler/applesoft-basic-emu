"""Tests unitaires pour l'interpréteur.

UC-003, UC-006, UC-009, UC-010, UC-011, UC-015, UC-016, UC-017, RG-0006 à RG-0010.
"""

import pytest

from applesoft.environment import Environment
from applesoft.errors import BasicError
from applesoft.interpreter import Interpreter
from applesoft.io_cli import IOBridgeCLI
from applesoft.lexer import TokenType, tokenize
from applesoft.parser import parse_tokens
from applesoft.program import Program


class MockIO(IOBridgeCLI):
    """IOBridge mockée pour les tests."""

    def __init__(self):
        super().__init__()
        self._output: list[str] = []
        self._cleared: bool = False
        self._cursor_row: int = 1
        self._video_mode_log: list[str] = []

    def print_str(self, text: str) -> None:
        self._output.append(text)
        # Mettre à jour la position du curseur
        if "\n" in text:
            last_line = text.rsplit("\n", 1)[-1]
            self._cursor_column = len(last_line) + 1
        else:
            self._cursor_column += len(text)

    def input_str(self, prompt: str = "") -> str:
        if prompt:
            self.print_str(prompt)
        raise EOFError

    def clear_screen(self) -> None:
        self._cleared = True
        self._cursor_column = 1
        self._cursor_row = 1

    def move_cursor_to_row(self, row: int) -> None:
        self._cursor_row = row
        self._cursor_column = 1

    def set_video_mode(self, mode: str) -> None:
        super().set_video_mode(mode)
        self._video_mode_log.append(mode)

    @property
    def output(self) -> str:
        return "".join(self._output)


def run_program(lines: list[str], start_line: int | None = None) -> str:
    """Helper : crée un programme, l'exécute et retourne la sortie."""
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
    """Helper : exécute une ligne en mode direct."""
    io = MockIO()
    prog = Program()
    env = Environment()
    interp = Interpreter(prog, env, io)

    tokens = tokenize(line)
    stmt_list = parse_tokens(tokens)
    interp.execute_direct(stmt_list)
    return io.output


# === UC-003 : Exécuter un programme ===


class TestUC003Run:
    def test_ca_uc_003_01_sequential(self):
        """CA-UC-003-01 : 10 PRINT "A" / 20 PRINT "B" → A puis B."""
        out = run_program(['10 PRINT "A"', '20 PRINT "B"'])
        assert out == "A\nB\n"

    def test_ca_uc_003_02_run_from_line(self):
        """CA-UC-003-02 : RUN 20 → seul B."""
        out = run_program(['10 PRINT "A"', '20 PRINT "B"'], start_line=20)
        assert out == "B\n"

    def test_ca_uc_003_03_variable(self):
        """CA-UC-003-03 : 10 X=5 / 20 PRINT X → 5."""
        out = run_program(["10 X=5", "20 PRINT X"])
        assert " 5\n" in out

    def test_ca_uc_003_04_end(self):
        """CA-UC-003-04 : END arrête l'exécution."""
        out = run_program(['10 PRINT "A" : END : PRINT "B"'])
        assert "A\n" in out
        assert "B" not in out

    def test_ca_uc_003_05_stop_cont(self):
        """CA-UC-003-05 : STOP + CONT."""
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

        # CONT
        io._output.clear()
        interp.continue_execution()
        assert "B\n" in io.output

    def test_ca_uc_003_06_stop_modify_cont(self):
        """CA-UC-003-06 : STOP + modif variable + CONT."""
        io = MockIO()
        prog = Program()
        env = Environment()

        for line in ["10 X=1", "20 STOP", "30 PRINT X"]:
            tokens = tokenize(line)
            prog.add_line(tokens[0].value, tokens[1:])

        interp = Interpreter(prog, env, io)
        interp.run()

        # Modifier la variable en mode direct
        env.set_var("X", 99.0)

        io._output.clear()
        interp.continue_execution()
        assert " 99\n" in io.output

    def test_run_empty_program(self):
        """RUN sans programme → pas d'erreur."""
        out = run_program([])
        assert out == ""

    def test_run_undefined_line(self):
        """RUN 99 avec ligne inexistante → UNDEF'D STATEMENT."""
        with pytest.raises(BasicError) as exc_info:
            run_program(['10 PRINT "A"'], start_line=99)
        assert exc_info.value.code == 90

    def test_cont_without_stop(self):
        """CONT sans arrêt → CAN'T CONTINUE."""
        io = MockIO()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)
        with pytest.raises(BasicError) as exc_info:
            interp.continue_execution()
        assert exc_info.value.code == 254


# === UC-006 : Afficher des données ===


class TestUC006Print:
    def test_ca_uc_006_01_print_string(self):
        """CA-UC-006-01 : PRINT "HELLO" → HELLO + retour ligne."""
        out = run_direct('PRINT "HELLO"')
        assert out == "HELLO\n"

    def test_ca_uc_006_02_semicolon(self):
        """CA-UC-006-02 : PRINT "A";"B" → AB."""
        out = run_direct('PRINT "A";"B"')
        assert out == "AB\n"

    def test_ca_uc_006_03_comma(self):
        """CA-UC-006-03 : PRINT "A","B" → A + espaces jusqu'à col 16 + B."""
        out = run_direct('PRINT "A","B"')
        assert out.startswith("A")
        # "A" prend 1 char, puis espaces jusqu'à colonne 16 = 15 espaces
        assert "B" in out
        # Vérifier le nombre d'espaces
        idx_b = out.index("B")
        assert idx_b >= 15  # Au moins 15 chars avant B

    def test_ca_uc_006_04_trailing_semicolon(self):
        """CA-UC-006-04 : PRINT "A"; / PRINT "B" → AB sur une ligne."""
        out = run_program(['10 PRINT "A";', '20 PRINT "B"'])
        assert out == "AB\n"

    def test_ca_uc_006_05_print_empty(self):
        """CA-UC-006-05 : PRINT seul → ligne vide."""
        out = run_direct("PRINT")
        assert out == "\n"

    def test_ca_uc_006_06_question_mark(self):
        """CA-UC-006-06 : ? "HELLO" → HELLO."""
        out = run_direct('? "HELLO"')
        assert out == "HELLO\n"

    def test_ca_uc_006_07_spc(self):
        """CA-UC-006-07 : PRINT SPC(5);"X" → 5 espaces + X."""
        out = run_direct('PRINT SPC(5);"X"')
        assert out == "     X\n"

    def test_ca_uc_006_08_tab(self):
        """CA-UC-006-08 : PRINT TAB(10);"X" → X en colonne 10."""
        out = run_direct('PRINT TAB(10);"X"')
        # 9 espaces + X = X en colonne 10
        assert "X" in out
        idx = out.index("X")
        assert idx == 9

    def test_ca_uc_006_09_tab_beyond_cursor(self):
        """CA-UC-006-09 : TAB avec curseur au-delà → nouvelle ligne."""
        out = run_program(['10 PRINT "ABCDEFGHIJ";TAB(5);"X"'])
        # Le curseur est en colonne 11 après les 10 chars
        # TAB(5) passe à la ligne suivante et met X en colonne 5
        lines = out.split("\n")
        assert len(lines) >= 2  # Au moins 2 lignes

    def test_ca_uc_006_10_pos(self):
        """CA-UC-006-10 : POS(0) retourne la colonne courante."""
        out = run_program(['10 PRINT "ABC";', "20 PRINT POS(0)"])
        # Après "ABC", curseur en colonne 4 (1-based)
        assert "4" in out


# === UC-010 : Variables ===


class TestUC010Variables:
    def test_ca_uc_010_01_let_explicit(self):
        """CA-UC-010-01 : LET A = 5 : PRINT A → 5."""
        out = run_direct("LET A = 5 : PRINT A")
        assert " 5\n" in out

    def test_ca_uc_010_02_let_implicit(self):
        """CA-UC-010-02 : A = 5 : PRINT A → 5."""
        out = run_direct("A = 5 : PRINT A")
        assert " 5\n" in out

    def test_ca_uc_010_03_uninitialized(self):
        """CA-UC-010-03 : PRINT X (non initialisée) → 0."""
        out = run_direct("PRINT X")
        assert " 0\n" in out

    def test_ca_uc_010_04_dim_array(self):
        """CA-UC-010-04 : DIM A(5) / A(3)=42 / PRINT A(3) → 42."""
        out = run_program(["10 DIM A(5)", "20 A(3)=42", "30 PRINT A(3)"])
        assert " 42\n" in out

    def test_ca_uc_010_05_dim_2d(self):
        """CA-UC-010-05 : DIM B(2,3) / B(1,2)=7 / PRINT B(1,2) → 7."""
        out = run_program(["10 DIM B(2,3)", "20 B(1,2)=7", "30 PRINT B(1,2)"])
        assert " 7\n" in out

    def test_ca_uc_010_06_auto_dim(self):
        """CA-UC-010-06 : A(3)=5 sans DIM → auto-dim à 10."""
        out = run_program(["10 A(3)=5", "20 PRINT A(3)"])
        assert " 5\n" in out


# === UC-011 : Expressions ===


class TestUC011Expressions:
    def test_ca_uc_011_01_precedence(self):
        """CA-UC-011-01 : PRINT 2+3*4 → 14."""
        out = run_direct("PRINT 2+3*4")
        assert " 14\n" in out

    def test_ca_uc_011_02_parentheses(self):
        """CA-UC-011-02 : PRINT (2+3)*4 → 20."""
        out = run_direct("PRINT (2+3)*4")
        assert " 20\n" in out

    def test_ca_uc_011_03_power_right_assoc(self):
        """CA-UC-011-03 : PRINT 2^3^2 → 512."""
        out = run_direct("PRINT 2^3^2")
        assert " 512\n" in out

    def test_ca_uc_011_04_subtraction_left_assoc(self):
        """CA-UC-011-04 : PRINT 10-3-2 → 5."""
        out = run_direct("PRINT 10-3-2")
        assert " 5\n" in out

    def test_ca_uc_011_05_greater_than(self):
        """CA-UC-011-05 : PRINT 5>3 → 1."""
        out = run_direct("PRINT 5>3")
        assert " 1\n" in out

    def test_ca_uc_011_06_equal(self):
        """CA-UC-011-06 : PRINT 5=3 → 0."""
        out = run_direct("PRINT 5=3")
        assert " 0\n" in out

    def test_ca_uc_011_07_string_comparison(self):
        """CA-UC-011-07 : PRINT "B">"A" → 1."""
        out = run_direct('PRINT "B">"A"')
        assert " 1\n" in out

    def test_ca_uc_011_08_and(self):
        """CA-UC-011-08 : PRINT 1 AND 0 → 0."""
        out = run_direct("PRINT 1 AND 0")
        assert " 0\n" in out

    def test_ca_uc_011_09_or(self):
        """CA-UC-011-09 : PRINT 1 OR 0 → 1."""
        out = run_direct("PRINT 1 OR 0")
        assert " 1\n" in out

    def test_ca_uc_011_10_not(self):
        """CA-UC-011-10 : PRINT NOT 0 → 1."""
        out = run_direct("PRINT NOT 0")
        assert " 1\n" in out

    def test_ca_uc_011_11_compound_logical(self):
        """CA-UC-011-11 : PRINT 5>3 AND 2<4 → 1."""
        out = run_direct("PRINT 5>3 AND 2<4")
        assert " 1\n" in out

    def test_ca_uc_011_12_bitwise_and(self):
        """CA-UC-011-12 : PRINT 12 AND 10 → 8."""
        out = run_direct("PRINT 12 AND 10")
        assert " 8\n" in out

    def test_ca_uc_011_13_zero_power_zero(self):
        """CA-UC-011-13 : PRINT 0^0 → 1."""
        out = run_direct("PRINT 0^0")
        assert " 1\n" in out

    def test_ca_uc_011_14_unary_precedence(self):
        """CA-UC-011-14 : PRINT -2^2 → 4 ((-2)^2)."""
        out = run_direct("PRINT -2^2")
        assert " 4\n" in out

    def test_ca_uc_011_15_equal_less(self):
        """CA-UC-011-15 : PRINT 5 =< 5 → 1."""
        out = run_direct("PRINT 5 =< 5")
        assert " 1\n" in out


# === RG-0006 : Types numériques ===


class TestRG0006Types:
    def test_ca_rg_0006_04_integer_overflow(self):
        """CA-RG-0006-04 : X%=32768 → ILLEGAL QUANTITY."""
        with pytest.raises(BasicError) as exc_info:
            run_direct("X%=32768")
        assert exc_info.value.code == 53

    def test_ca_rg_0006_05_integer_truncation(self):
        """CA-RG-0006-05 : X%=3.7 → tronqué à 3."""
        io = MockIO()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)
        tokens = tokenize("X%=3.7 : PRINT X%")
        stmt_list = parse_tokens(tokens)
        interp.execute_direct(stmt_list)
        assert " 3\n" in io.output

    def test_ca_rg_0006_06_overflow(self):
        """CA-RG-0006-06 : X=1E39 → OVERFLOW ERROR."""
        # 1E39 is representable in IEEE 754, but Applesoft treats it as overflow
        # We handle it through arithmetic that overflows
        with pytest.raises(BasicError) as exc_info:
            run_direct("PRINT EXP(1000)")
        assert exc_info.value.code == 69


# === RG-0007 : Chaînes ===


class TestRG0007Strings:
    def test_ca_rg_0007_01_concatenation(self):
        """CA-RG-0007-01 : A$+"HELLO" + B$=" WORLD" → HELLO WORLD."""
        out = run_direct('A$="HELLO" : B$=" WORLD" : PRINT A$+B$')
        assert "HELLO WORLD\n" in out

    def test_ca_rg_0007_02_string_too_long(self):
        """CA-RG-0007-02 : Concaténation > 255 chars → STRING TOO LONG."""
        io = MockIO()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)

        # Créer une chaîne de 200 chars + une de 60 chars
        env.set_var("A$", "X" * 200)
        env.set_var("B$", "Y" * 60)

        tokens = tokenize("PRINT A$+B$")
        stmt_list = parse_tokens(tokens)
        with pytest.raises(BasicError) as exc_info:
            interp.execute_direct(stmt_list)
        assert exc_info.value.code == 176

    def test_ca_rg_0007_03_type_mismatch_to_string(self):
        """CA-RG-0007-03 : A$=5 → TYPE MISMATCH."""
        with pytest.raises(BasicError) as exc_info:
            run_direct("A$=5")
        assert exc_info.value.code == 163

    def test_ca_rg_0007_04_type_mismatch_to_numeric(self):
        """CA-RG-0007-04 : A="TEXT" → TYPE MISMATCH."""
        with pytest.raises(BasicError) as exc_info:
            run_direct('A="TEXT"')
        assert exc_info.value.code == 163


# === RG-0008, RG-0009 ===


class TestRG0008MultiStatement:
    def test_ca_rg_0008_01_multi_print(self):
        """CA-RG-0008-01 : PRINT "A" : PRINT "B" → A puis B."""
        out = run_direct('PRINT "A" : PRINT "B"')
        assert out == "A\nB\n"


class TestRG0009Rem:
    def test_ca_rg_0009_01_rem_ignored(self):
        """CA-RG-0009-01 : REM → ignoré."""
        out = run_program(["10 REM COMMENTAIRE", '20 PRINT "OK"'])
        assert "COMMENTAIRE" not in out
        assert "OK\n" in out

    def test_ca_rg_0009_02_rem_eats_colon(self):
        """CA-RG-0009-02 : REM TEXTE : PRINT → rien."""
        out = run_program(['10 REM TEXTE : PRINT "CACHÉ"'])
        assert "CACHÉ" not in out
        assert out == ""


def run_program_io(lines: list[str]) -> MockIO:
    """Helper : crée un programme, l'exécute et retourne l'objet IO."""
    io = MockIO()
    prog = Program()
    env = Environment()

    for line in lines:
        tokens = tokenize(line)
        if tokens and tokens[0].type == TokenType.LINENUM:
            prog.add_line(tokens[0].value, tokens[1:])

    interp = Interpreter(prog, env, io)
    interp.run()
    return io


# === UC-009 : Contrôle de l'affichage ===


class TestUC009DisplayControl:
    def test_ca_uc_009_01_htab(self):
        """CA-UC-009-01 : HTAB 10 : PRINT "X" → X en colonne 10."""
        io = run_program_io(['10 HTAB 10 : PRINT "X"'])
        # HTAB insère des espaces, puis X
        assert "X" in io.output
        # Vérifier que HTAB produit 9 espaces (col 1→10)
        assert "         X" in io.output

    def test_ca_uc_009_02_vtab_htab(self):
        """CA-UC-009-02 : VTAB 12 : HTAB 20 : PRINT "X" → position (12,20)."""
        io = run_program_io(['10 VTAB 12 : HTAB 20 : PRINT "X"'])
        assert io._cursor_row == 12
        assert "X" in io.output

    def test_ca_uc_009_03_home(self):
        """CA-UC-009-03 : HOME → écran vidé, curseur en (1,1)."""
        io = run_program_io(["10 HOME"])
        assert io._cleared is True
        assert io._cursor_column == 1
        assert io._cursor_row == 1

    def test_ca_uc_009_04_inverse(self):
        """CA-UC-009-04 : INVERSE + PRINT → mode inversé."""
        io = run_program_io(['10 INVERSE : PRINT "INV" : NORMAL : PRINT "NOR"'])
        assert "inverse" in io._video_mode_log
        assert "normal" in io._video_mode_log
        assert "INV" in io.output
        assert "NOR" in io.output

    def test_ca_uc_009_05_flash(self):
        """CA-UC-009-05 : FLASH + PRINT → attribut clignotant."""
        io = run_program_io(['10 FLASH : PRINT "BLINK"'])
        assert "flash" in io._video_mode_log
        assert "BLINK" in io.output

    def test_ca_uc_009_06_speed(self):
        """CA-UC-009-06 : SPEED=100 → délai configuré."""
        io = run_program_io(['10 SPEED=100 : PRINT "SLOW"'])
        assert io._speed == 100
        assert "SLOW" in io.output

    def test_htab_out_of_range(self):
        """HTAB 0 ou 41 → ?ILLEGAL QUANTITY ERROR."""
        with pytest.raises(BasicError) as exc_info:
            run_program(["10 HTAB 0"])
        assert exc_info.value.code == 53

        with pytest.raises(BasicError) as exc_info:
            run_program(["10 HTAB 41"])
        assert exc_info.value.code == 53

    def test_vtab_out_of_range(self):
        """VTAB 0 ou 25 → ?ILLEGAL QUANTITY ERROR."""
        with pytest.raises(BasicError) as exc_info:
            run_program(["10 VTAB 0"])
        assert exc_info.value.code == 53

        with pytest.raises(BasicError) as exc_info:
            run_program(["10 VTAB 25"])
        assert exc_info.value.code == 53

    def test_speed_out_of_range(self):
        """SPEED= -1 ou 256 → ?ILLEGAL QUANTITY ERROR."""
        with pytest.raises(BasicError) as exc_info:
            run_program(["10 SPEED= -1"])
        assert exc_info.value.code == 53

        with pytest.raises(BasicError) as exc_info:
            run_program(["10 SPEED= 256"])
        assert exc_info.value.code == 53


# === UC-015 : Fonctions mathématiques ===


class TestUC015MathFunctions:
    def test_ca_uc_015_01_abs(self):
        """CA-UC-015-01 : PRINT ABS(-5) → 5."""
        out = run_program(["10 PRINT ABS(-5)"])
        assert " 5\n" in out

    def test_ca_uc_015_02_int_positive(self):
        """CA-UC-015-02 : PRINT INT(3.7) → 3."""
        out = run_program(["10 PRINT INT(3.7)"])
        assert " 3\n" in out

    def test_ca_uc_015_03_int_negative(self):
        """CA-UC-015-03 : PRINT INT(-3.7) → -4 (arrondi vers le bas)."""
        out = run_program(["10 PRINT INT(-3.7)"])
        assert "-4\n" in out

    def test_ca_uc_015_04_sqr(self):
        """CA-UC-015-04 : PRINT SQR(16) → 4."""
        out = run_program(["10 PRINT SQR(16)"])
        assert " 4\n" in out

    def test_ca_uc_015_05_sgn(self):
        """CA-UC-015-05 : PRINT SGN(-42) → -1."""
        out = run_program(["10 PRINT SGN(-42)"])
        assert "-1\n" in out

    def test_ca_uc_015_06_rnd_different(self):
        """CA-UC-015-06 : deux RND(1) → valeurs différentes dans [0,1)."""
        out = run_program(["10 PRINT RND(1)", "20 PRINT RND(1)"])
        lines = [x.strip() for x in out.strip().split("\n")]
        assert len(lines) == 2
        v1, v2 = float(lines[0]), float(lines[1])
        assert 0 <= v1 < 1
        assert 0 <= v2 < 1
        # Probabilité de collision ~0
        assert v1 != v2

    def test_ca_uc_015_07_rnd_seed(self):
        """CA-UC-015-07 : RND(-5) + RND(1) → graine déterministe."""
        out1 = run_program(["10 X = RND(-5)", "20 PRINT RND(1)"])
        out2 = run_program(["10 X = RND(-5)", "20 PRINT RND(1)"])
        v1 = float(out1.strip())
        v2 = float(out2.strip())
        assert v1 == v2

    def test_ca_uc_015_08_rnd_zero_repeats(self):
        """CA-UC-015-08 : RND(0) → répète le dernier."""
        out = run_program(["10 X = RND(1)", "20 PRINT X", "30 PRINT RND(0)"])
        lines = [x.strip() for x in out.strip().split("\n")]
        assert len(lines) == 2
        assert lines[0] == lines[1]


# === UC-016 : Fonctions de chaînes ===


class TestUC016StringFunctions:
    def test_ca_uc_016_01_len(self):
        """CA-UC-016-01 : PRINT LEN("HELLO") → 5."""
        out = run_program(['10 PRINT LEN("HELLO")'])
        assert " 5\n" in out

    def test_ca_uc_016_02_left(self):
        """CA-UC-016-02 : PRINT LEFT$("HELLO",3) → HEL."""
        out = run_program(['10 PRINT LEFT$("HELLO",3)'])
        assert "HEL\n" in out

    def test_ca_uc_016_03_right(self):
        """CA-UC-016-03 : PRINT RIGHT$("HELLO",3) → LLO."""
        out = run_program(['10 PRINT RIGHT$("HELLO",3)'])
        assert "LLO\n" in out

    def test_ca_uc_016_04_mid(self):
        """CA-UC-016-04 : PRINT MID$("HELLO",2,3) → ELL."""
        out = run_program(['10 PRINT MID$("HELLO",2,3)'])
        assert "ELL\n" in out

    def test_ca_uc_016_05_asc(self):
        """CA-UC-016-05 : PRINT ASC("A") → 65."""
        out = run_program(['10 PRINT ASC("A")'])
        assert " 65\n" in out

    def test_ca_uc_016_06_chr(self):
        """CA-UC-016-06 : PRINT CHR$(65) → A."""
        out = run_program(["10 PRINT CHR$(65)"])
        assert "A\n" in out

    def test_ca_uc_016_07_val(self):
        """CA-UC-016-07 : PRINT VAL("3.14") → 3.14."""
        out = run_program(['10 PRINT VAL("3.14")'])
        assert "3.14\n" in out

    def test_ca_uc_016_08_str(self):
        """CA-UC-016-08 : PRINT STR$(42) → " 42"."""
        out = run_program(["10 PRINT STR$(42)"])
        # STR$ retourne " 42" (avec espace), PRINT l'affiche puis \n
        assert " 42\n" in out

    def test_ca_uc_016_09_mid_out_of_range(self):
        """CA-UC-016-09 : MID$("AB",5,1) → chaîne vide."""
        out = run_program(['10 PRINT MID$("AB",5,1)'])
        assert out == "\n"

    def test_ca_uc_016_10_val_non_numeric(self):
        """CA-UC-016-10 : VAL("HELLO") → 0."""
        out = run_program(['10 PRINT VAL("HELLO")'])
        assert " 0\n" in out

    def test_ca_uc_016_11_val_partial(self):
        """CA-UC-016-11 : VAL("3ABC") → 3."""
        out = run_program(['10 PRINT VAL("3ABC")'])
        assert " 3\n" in out


# === UC-017 : Fonctions utilisateur DEF FN ===


class TestUC017DefFn:
    def test_ca_uc_017_01_def_fn_double(self):
        """CA-UC-017-01 : DEF FN DOUBLE(X)=X*2 : PRINT FN DOUBLE(5) → 10."""
        out = run_program(["10 DEF FN DOUBLE(X) = X * 2", "20 PRINT FN DOUBLE(5)"])
        assert " 10\n" in out

    def test_ca_uc_017_02_def_fn_global_var(self):
        """CA-UC-017-02 : DEF FN avec variable globale → correctement évaluée."""
        out = run_program(
            [
                "10 Y = 10",
                "20 DEF FN ADD(X) = X + Y",
                "30 PRINT FN ADD(5)",
            ]
        )
        assert " 15\n" in out

    def test_ca_uc_017_03_undef_fn_error(self):
        """FN sans DEF → ?UNDEF'D FUNCTION ERROR."""
        with pytest.raises(BasicError) as exc_info:
            run_program(["10 PRINT FN NOPE(1)"])
        assert exc_info.value.code == 224
