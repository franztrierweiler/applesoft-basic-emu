"""Tests QA — Lot 04 : fonctions intégrées, affichage avancé, persistance.

Scénarios issus de qa/plan-test/lot-04-fonctions-affichage-persistance.md
"""

from __future__ import annotations

import math
import os
import tempfile

import pytest

from applesoft.environment import Environment
from applesoft.errors import BasicError
from applesoft.interpreter import Interpreter
from applesoft.io_cli import IOBridgeCLI
from applesoft.lexer import tokenize
from applesoft.parser import parse_tokens
from applesoft.program import Program
from applesoft.repl import REPL

# --- Helpers ---


def _run_program(lines: dict[int, str]) -> str:
    """Exécute un programme et retourne la sortie."""
    io = IOBridgeCLI()
    output: list[str] = []
    io.print_str = lambda text: output.append(text)
    io.clear_screen = lambda: output.append("[CLS]")
    io.move_cursor_to_row = lambda r: output.append(f"[VTAB:{r}]")

    env = Environment()
    prog = Program()
    for num, src in sorted(lines.items()):
        tokens = tokenize(src)
        prog.add_line(num, tokens)
    interp = Interpreter(prog, env, io)
    interp.run()
    return "".join(output)


def _run_direct(src: str) -> str:
    """Exécute une instruction directe et retourne la sortie."""
    io = IOBridgeCLI()
    output: list[str] = []
    io.print_str = lambda text: output.append(text)
    io.clear_screen = lambda: output.append("[CLS]")

    env = Environment()
    prog = Program()
    interp = Interpreter(prog, env, io)
    tokens = tokenize(src)
    stmt_list = parse_tokens(tokens)
    interp.execute_direct(stmt_list)
    return "".join(output)


def _make_repl(output: list[str], file_dir: str | None = None) -> REPL:
    """Crée un REPL avec sortie capturée."""
    io = IOBridgeCLI()
    io.print_str = lambda text: output.append(text)
    repl = REPL(io, file_dir=file_dir)
    return repl


def _repl_direct(repl: REPL, src: str) -> None:
    """Envoie une commande directe au REPL (tokenisée)."""
    repl._process_line(src)


# === T01 — UC-015 : Fonctions mathématiques ===


class TestT01MathFunctions:
    """Scénarios QA pour UC-015."""

    def test_t01_01_abs(self):
        """T01-01 [🔴] ABS(-5) → 5."""
        out = _run_direct("PRINT ABS(-5)")
        assert out.strip() == "5"

    def test_t01_02_int_positive(self):
        """T01-02 [🔴] INT(3.7) → 3."""
        out = _run_direct("PRINT INT(3.7)")
        assert out.strip() == "3"

    def test_t01_03_int_negative(self):
        """T01-03 [🔴] INT(-3.7) → -4 (arrondi vers le bas)."""
        out = _run_direct("PRINT INT(-3.7)")
        assert out.strip() == "-4"

    def test_t01_04_sqr(self):
        """T01-04 [🔴] SQR(16) → 4."""
        out = _run_direct("PRINT SQR(16)")
        assert out.strip() == "4"

    def test_t01_05_sgn(self):
        """T01-05 [🔴] SGN(-42) → -1, SGN(0) → 0, SGN(5) → 1."""
        out = _run_direct("PRINT SGN(-42)")
        assert out.strip() == "-1"
        out = _run_direct("PRINT SGN(0)")
        assert out.strip() == "0"
        out = _run_direct("PRINT SGN(5)")
        assert out.strip() == "1"

    def test_t01_06_rnd_different(self):
        """T01-06 [🔴] RND(1) → deux valeurs différentes ∈ [0,1)."""
        out1 = _run_program({10: "PRINT RND(1)"})
        out2 = _run_program({10: "PRINT RND(1)"})
        v1 = float(out1.strip())
        v2 = float(out2.strip())
        assert 0 <= v1 < 1
        assert 0 <= v2 < 1

    def test_t01_07_rnd_seed(self):
        """T01-07 [🟠] RND(-5) + RND(1) → graine déterministe."""
        out1 = _run_program({10: "X = RND(-5) : PRINT RND(1)"})
        out2 = _run_program({10: "X = RND(-5) : PRINT RND(1)"})
        assert out1.strip() == out2.strip()

    def test_t01_08_rnd_zero_repeats(self):
        """T01-08 [🟠] RND(0) → répète le dernier."""
        out = _run_program({10: "X = RND(1) : PRINT RND(0)"})
        lines = out.strip().split("\n")
        assert len(lines) == 1

    def test_t01_09_sqr_negative(self):
        """T01-09 [🔴] SQR(-1) → ?ILLEGAL QUANTITY ERROR."""
        with pytest.raises(BasicError) as exc:
            _run_direct("PRINT SQR(-1)")
        assert exc.value.code == 53

    def test_t01_10_log_zero(self):
        """T01-10 [🔴] LOG(0) → ?ILLEGAL QUANTITY ERROR."""
        with pytest.raises(BasicError) as exc:
            _run_direct("PRINT LOG(0)")
        assert exc.value.code == 53

    def test_t01_11_log_negative(self):
        """T01-11 [🔴] LOG(-1) → ?ILLEGAL QUANTITY ERROR."""
        with pytest.raises(BasicError) as exc:
            _run_direct("PRINT LOG(-1)")
        assert exc.value.code == 53

    def test_t01_12_trig_and_log_exp(self):
        """T01-12 [🟠] LOG, EXP, SIN, COS, TAN, ATN — valeurs de référence."""
        out = _run_direct("PRINT LOG(1)")
        assert float(out.strip()) == pytest.approx(0.0)
        out = _run_direct("PRINT EXP(0)")
        assert float(out.strip()) == pytest.approx(1.0)
        out = _run_direct("PRINT SIN(0)")
        assert float(out.strip()) == pytest.approx(0.0)
        out = _run_direct("PRINT COS(0)")
        assert float(out.strip()) == pytest.approx(1.0)
        out = _run_direct("PRINT TAN(0)")
        assert float(out.strip()) == pytest.approx(0.0)
        out = _run_direct("PRINT ATN(1)")
        assert float(out.strip()) == pytest.approx(math.pi / 4, rel=1e-6)


# === T02 — UC-016 : Fonctions de chaînes ===


class TestT02StringFunctions:
    """Scénarios QA pour UC-016."""

    def test_t02_01_len(self):
        """T02-01 [🔴] LEN("HELLO") → 5."""
        out = _run_direct('PRINT LEN("HELLO")')
        assert out.strip() == "5"

    def test_t02_02_left(self):
        """T02-02 [🔴] LEFT$("HELLO",3) → "HEL"."""
        out = _run_direct('PRINT LEFT$("HELLO",3)')
        assert out.strip() == "HEL"

    def test_t02_03_right(self):
        """T02-03 [🔴] RIGHT$("HELLO",3) → "LLO"."""
        out = _run_direct('PRINT RIGHT$("HELLO",3)')
        assert out.strip() == "LLO"

    def test_t02_04_mid(self):
        """T02-04 [🔴] MID$("HELLO",2,3) → "ELL"."""
        out = _run_direct('PRINT MID$("HELLO",2,3)')
        assert out.strip() == "ELL"

    def test_t02_05_asc(self):
        """T02-05 [🔴] ASC("A") → 65."""
        out = _run_direct('PRINT ASC("A")')
        assert out.strip() == "65"

    def test_t02_06_chr(self):
        """T02-06 [🔴] CHR$(65) → "A"."""
        out = _run_direct("PRINT CHR$(65)")
        assert out.strip() == "A"

    def test_t02_07_val(self):
        """T02-07 [🔴] VAL("3.14") → 3.14."""
        out = _run_direct('PRINT VAL("3.14")')
        assert float(out.strip()) == pytest.approx(3.14)

    def test_t02_08_str(self):
        """T02-08 [🔴] STR$(42) → " 42"."""
        out = _run_direct("PRINT STR$(42)")
        assert " 42" in out

    def test_t02_09_mid_out_of_range(self):
        """T02-09 [🟠] MID$("AB",5,1) → chaîne vide."""
        out = _run_direct('PRINT MID$("AB",5,1)')
        assert out.strip() == ""

    def test_t02_10_val_non_numeric(self):
        """T02-10 [🟠] VAL("HELLO") → 0."""
        out = _run_direct('PRINT VAL("HELLO")')
        assert float(out.strip()) == 0.0

    def test_t02_11_val_partial(self):
        """T02-11 [🟠] VAL("3ABC") → 3."""
        out = _run_direct('PRINT VAL("3ABC")')
        assert float(out.strip()) == 3.0

    def test_t02_12_asc_empty(self):
        """T02-12 [🔴] ASC("") → ?ILLEGAL QUANTITY ERROR."""
        with pytest.raises(BasicError) as exc:
            _run_direct('PRINT ASC("")')
        assert exc.value.code == 53

    def test_t02_13_chr_overflow(self):
        """T02-13 [🔴] CHR$(256) → ?ILLEGAL QUANTITY ERROR."""
        with pytest.raises(BasicError) as exc:
            _run_direct("PRINT CHR$(256)")
        assert exc.value.code == 53

    def test_t02_14_left_negative(self):
        """T02-14 [🔴] LEFT$("HI",-1) → ?ILLEGAL QUANTITY ERROR."""
        with pytest.raises(BasicError) as exc:
            _run_direct('PRINT LEFT$("HI",-1)')
        assert exc.value.code == 53

    def test_t02_15_mid_no_length(self):
        """T02-15 [🟠] MID$ sans longueur → retourne jusqu'à la fin."""
        out = _run_direct('PRINT MID$("HELLO",3)')
        assert out.strip() == "LLO"


# === T03 — UC-017 : DEF FN ===


class TestT03DefFn:
    """Scénarios QA pour UC-017."""

    def test_t03_01_def_fn_double(self):
        """T03-01 [🔴] DEF FN DOUBLE(X)=X*2 → 10."""
        out = _run_program(
            {
                10: "DEF FN DOUBLE(X) = X * 2",
                20: "PRINT FN DOUBLE(5)",
            }
        )
        assert out.strip() == "10"

    def test_t03_02_def_fn_global_var(self):
        """T03-02 [🔴] DEF FN avec variable globale → 15."""
        out = _run_program(
            {
                10: "Y = 10",
                20: "DEF FN ADD(X) = X + Y",
                30: "PRINT FN ADD(5)",
            }
        )
        assert out.strip() == "15"

    def test_t03_03_undef_fn_error(self):
        """T03-03 [🔴] FN sans DEF → ?UNDEF'D FUNCTION ERROR."""
        with pytest.raises(BasicError) as exc:
            _run_program({10: "PRINT FN DOUBLE(5)"})
        assert exc.value.code == 224

    def test_t03_04_fn_error_at_call(self):
        """T03-04 [🟠] DEF FN avec erreur → erreur à l'appel, pas à la définition."""
        # Pas d'erreur à la définition
        _run_program({10: "DEF FN BAD(X) = X / 0"})  # Pas de crash
        # Erreur à l'appel
        with pytest.raises(BasicError) as exc:
            _run_program(
                {
                    10: "DEF FN BAD(X) = X / 0",
                    20: "PRINT FN BAD(5)",
                }
            )
        assert exc.value.code == 133


# === T04 — UC-009 : Contrôle de l'affichage ===


class TestT04DisplayControl:
    """Scénarios QA pour UC-009."""

    def test_t04_01_htab(self):
        """T04-01 [🔴] HTAB 10 → colonne 10."""
        io = IOBridgeCLI()
        output: list[str] = []
        io.print_str = lambda text: output.append(text)

        env = Environment()
        prog = Program()
        tokens = tokenize('HTAB 10 : PRINT "X"')
        stmt_list = parse_tokens(tokens)
        interp = Interpreter(prog, env, io)
        interp.execute_direct(stmt_list)
        full = "".join(output)
        assert "X" in full
        idx = full.index("X")
        assert idx >= 8

    def test_t04_02_vtab_htab(self):
        """T04-02 [🔴] VTAB 12 : HTAB 20 → position correcte."""
        out = _run_program({10: 'VTAB 12 : HTAB 20 : PRINT "X"'})
        assert "[VTAB:12]" in out
        assert "X" in out

    def test_t04_03_home(self):
        """T04-03 [🔴] HOME → écran vidé."""
        out = _run_program({10: "HOME"})
        assert "[CLS]" in out

    def test_t04_04_inverse(self):
        """T04-04 [🟠] INVERSE + PRINT → mode inversé."""
        io = IOBridgeCLI()
        output: list[str] = []
        io.print_str = lambda text: output.append(text)

        env = Environment()
        prog = Program()
        interp = Interpreter(prog, env, io)
        tokens = tokenize('INVERSE : PRINT "INV" : NORMAL : PRINT "NOR"')
        stmt_list = parse_tokens(tokens)
        assert io._video_mode == "normal"
        interp.execute_direct(stmt_list)
        assert io._video_mode == "normal"

    def test_t04_05_flash(self):
        """T04-05 [🟠] FLASH + PRINT → attribut clignotant."""
        io = IOBridgeCLI()
        output: list[str] = []
        io.print_str = lambda text: output.append(text)

        env = Environment()
        prog = Program()
        interp = Interpreter(prog, env, io)
        tokens = tokenize('FLASH : PRINT "BLINK"')
        stmt_list = parse_tokens(tokens)
        interp.execute_direct(stmt_list)
        assert io._video_mode == "flash"

    def test_t04_06_speed(self):
        """T04-06 [🟡] SPEED=100 → délai configuré."""
        io = IOBridgeCLI()
        output: list[str] = []
        io.print_str = lambda text: output.append(text)

        env = Environment()
        prog = Program()
        interp = Interpreter(prog, env, io)
        tokens = tokenize("SPEED=100")
        stmt_list = parse_tokens(tokens)
        interp.execute_direct(stmt_list)
        assert io._speed == 100

    def test_t04_07_htab_out_of_range(self):
        """T04-07 [🔴] HTAB 0 / HTAB 41 → ?ILLEGAL QUANTITY ERROR."""
        with pytest.raises(BasicError) as exc:
            _run_direct("HTAB 0")
        assert exc.value.code == 53
        with pytest.raises(BasicError) as exc:
            _run_direct("HTAB 41")
        assert exc.value.code == 53

    def test_t04_08_vtab_out_of_range(self):
        """T04-08 [🔴] VTAB 0 / VTAB 25 → ?ILLEGAL QUANTITY ERROR."""
        with pytest.raises(BasicError) as exc:
            _run_direct("VTAB 0")
        assert exc.value.code == 53
        with pytest.raises(BasicError) as exc:
            _run_direct("VTAB 25")
        assert exc.value.code == 53

    def test_t04_09_speed_out_of_range(self):
        """T04-09 [🟠] SPEED=-1 / SPEED=256 → ?ILLEGAL QUANTITY ERROR."""
        with pytest.raises(BasicError) as exc:
            _run_direct("SPEED= -1")
        assert exc.value.code == 53
        with pytest.raises(BasicError) as exc:
            _run_direct("SPEED= 256")
        assert exc.value.code == 53


# === T05 — UC-004 : SAVE ===


class TestT05Save:
    """Scénarios QA pour UC-004."""

    def test_t05_01_save_creates_file(self):
        """T05-01 [🔴] SAVE "TEST.BAS" → fichier texte créé."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output: list[str] = []
            io = IOBridgeCLI()
            io.print_str = lambda text: output.append(text)

            repl = REPL(io, file_dir=tmpdir)
            # Ajouter des lignes au programme
            tokens10 = tokenize('PRINT "A"')
            repl.program.add_line(10, tokens10)
            tokens20 = tokenize('PRINT "B"')
            repl.program.add_line(20, tokens20)

            _repl_direct(repl, 'SAVE "TEST.BAS"')
            filepath = os.path.join(tmpdir, "TEST.BAS")
            assert os.path.exists(filepath)
            content = open(filepath).read()
            assert "10" in content
            assert "20" in content

    def test_t05_02_save_no_filename(self):
        """T05-02 [🔴] SAVE sans nom → ?SYNTAX ERROR."""
        output: list[str] = []
        io = IOBridgeCLI()
        io.print_str = lambda text: output.append(text)

        repl = REPL(io)
        _repl_direct(repl, "SAVE")
        assert any("SYNTAX" in o for o in output)


# === T06 — UC-005 : LOAD ===


class TestT06Load:
    """Scénarios QA pour UC-005."""

    def test_t06_01_load_replaces_and_clears(self):
        """T06-01 [🔴] LOAD → programme chargé, variables effacées."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "TEST.BAS")
            with open(filepath, "w") as f:
                f.write('10 PRINT "A"\n20 PRINT "B"\n')

            output: list[str] = []
            io = IOBridgeCLI()
            io.print_str = lambda text: output.append(text)

            repl = REPL(io, file_dir=tmpdir)
            repl.env.set_var("X", 42)
            _repl_direct(repl, 'LOAD "TEST.BAS"')
            assert repl.program.has_line(10)
            assert repl.program.has_line(20)
            assert repl.env.get_var("X") == 0

    def test_t06_02_load_replaces_entirely(self):
        """T06-02 [🔴] LOAD → ancien programme intégralement remplacé."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "NEW.BAS")
            with open(filepath, "w") as f:
                f.write('10 PRINT "NEW"\n')

            output: list[str] = []
            io = IOBridgeCLI()
            io.print_str = lambda text: output.append(text)

            repl = REPL(io, file_dir=tmpdir)
            tokens = tokenize('PRINT "OLD"')
            repl.program.add_line(50, tokens)
            _repl_direct(repl, 'LOAD "NEW.BAS"')
            assert not repl.program.has_line(50)
            assert repl.program.has_line(10)

    def test_t06_03_load_file_not_found(self):
        """T06-03 [🔴] LOAD fichier inexistant → ?FILE NOT FOUND."""
        output: list[str] = []
        io = IOBridgeCLI()
        io.print_str = lambda text: output.append(text)

        repl = REPL(io)
        _repl_direct(repl, 'LOAD "NONEXISTENT.BAS"')
        assert any("FILE NOT FOUND" in o for o in output)

    def test_t06_04_load_path_traversal(self):
        """T06-04 [🔴] LOAD path traversal → bloqué (SEC-BP-22)."""
        output: list[str] = []
        io = IOBridgeCLI()
        io.print_str = lambda text: output.append(text)

        repl = REPL(io)
        _repl_direct(repl, 'LOAD "../../etc/passwd"')
        assert any("PATH NOT ALLOWED" in o or "ERROR" in o for o in output)
