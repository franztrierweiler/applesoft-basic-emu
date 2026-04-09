"""Tests QA — Lot 06 : graphisme (UC-018, UC-019, UC-020, UC-021).

Scénarios issus de qa/plan-test/lot-06-graphisme.md (44 scénarios).
Nommage : test_tXX_YY_description conforme au plan de test.
"""

from __future__ import annotations

import inspect

import pytest

from applesoft.environment import Environment
from applesoft.errors import BasicError
from applesoft.graphics import GraphicsEngine
from applesoft.interpreter import Interpreter
from applesoft.io_cli import IOBridgeCLI
from applesoft.lexer import tokenize
from applesoft.parser import parse_tokens
from applesoft.program import Program

# --- Helpers ---


def _run_program(lines: dict[int, str]) -> tuple[str, GraphicsEngine]:
    """Exécute un programme et retourne (sortie texte, moteur graphique)."""
    io = IOBridgeCLI()
    output: list[str] = []
    io.print_str = lambda text: output.append(text)
    io.clear_screen = lambda: output.append("[CLS]")

    env = Environment()
    prog = Program()
    gfx = GraphicsEngine()
    for num, src in sorted(lines.items()):
        tokens = tokenize(src)
        prog.add_line(num, tokens)
    interp = Interpreter(prog, env, io, graphics=gfx)
    interp.run()
    return "".join(output), gfx


def _run_direct(src: str, gfx: GraphicsEngine | None = None) -> tuple[str, GraphicsEngine]:
    """Exécute une instruction directe et retourne (sortie, moteur graphique)."""
    io = IOBridgeCLI()
    output: list[str] = []
    io.print_str = lambda text: output.append(text)

    env = Environment()
    prog = Program()
    if gfx is None:
        gfx = GraphicsEngine()
    interp = Interpreter(prog, env, io, graphics=gfx)
    tokens = tokenize(src)
    stmt_list = parse_tokens(tokens)
    interp.execute_direct(stmt_list)
    return "".join(output), gfx


def _run_direct_err(src: str, gfx: GraphicsEngine | None = None) -> BasicError:
    """Exécute une instruction directe et retourne l'erreur BasicError levée."""
    with pytest.raises(BasicError) as exc:
        _run_direct(src, gfx)
    return exc.value


def _make_shape_table() -> bytes:
    """Crée une shape table minimale avec 1 forme (un vecteur plot+haut)."""
    num_shapes = 1
    offset = 4  # header = 2 octets nb_shapes + 2 octets offset forme 1
    header = bytes(
        [
            num_shapes & 0xFF,
            (num_shapes >> 8) & 0xFF,
            offset & 0xFF,
            (offset >> 8) & 0xFF,
        ]
    )
    # Vecteur A : plot=1, dir=haut(00) -> bits 0-2 = 001 = 0x01, puis fin 0x00
    shape_data = bytes([0x01, 0x00])
    return header + shape_data


# ============================================================
# UC-018 — Dessiner en basse résolution (T01-01 à T01-16)
# ============================================================


class TestUC018LoRes:
    """16 scénarios QA pour UC-018 : basse résolution."""

    def test_t01_01_gr_active_lores(self):
        """T01-01 [Bloquant] GR active le mode LoRes (40x48), écran noir, couleur 0."""
        _, gfx = _run_direct("GR")
        assert gfx.mode == "lores"
        for y in range(48):
            for x in range(40):
                assert gfx.scrn(x, y) == 0

    def test_t01_02_plot_magenta(self):
        """T01-02 [Bloquant] GR : COLOR=1 : PLOT 5,5 place un bloc magenta en (5,5)."""
        _, gfx = _run_program({10: "GR : COLOR=1 : PLOT 5,5"})
        assert gfx.scrn(5, 5) == 1

    def test_t01_03_hlin_green(self):
        """T01-03 [Bloquant] GR : COLOR=4 : HLIN 0,39 AT 20 trace une ligne verte."""
        _, gfx = _run_program({10: "GR : COLOR=4 : HLIN 0,39 AT 20"})
        for x in range(40):
            assert gfx.scrn(x, 20) == 4

    def test_t01_04_hlin_inverted(self):
        """T01-04 [Bloquant] HLIN 30,10 AT 5 inverse les bornes et trace x=10 à x=30."""
        _, gfx = _run_program({10: "GR : COLOR=1 : HLIN 30,10 AT 5"})
        for x in range(10, 31):
            assert gfx.scrn(x, 5) == 1
        assert gfx.scrn(9, 5) == 0
        assert gfx.scrn(31, 5) == 0

    def test_t01_05_scrn_reads_color(self):
        """T01-05 [Bloquant] COLOR=9 : PLOT 5,5 : PRINT SCRN(5,5) affiche 9."""
        out, _ = _run_program({10: "GR : COLOR=9 : PLOT 5,5 : PRINT SCRN(5,5)"})
        assert out.strip() == "9"

    def test_t01_06_text_restores(self):
        """T01-06 [Bloquant] GR : PLOT 5,5 : TEXT : PRINT "BACK" restaure le mode texte."""
        out, gfx = _run_program(
            {
                10: "GR : COLOR=1 : PLOT 5,5",
                20: 'TEXT : PRINT "BACK"',
            }
        )
        assert gfx.mode == "text"
        assert "BACK" in out

    def test_t01_07_vlin_inverted(self):
        """T01-07 [Majeur] VLIN 30,10 AT 5 inverse les bornes et trace y=10 à y=30."""
        _, gfx = _run_program({10: "GR : COLOR=2 : VLIN 30,10 AT 5"})
        for y in range(10, 31):
            assert gfx.scrn(5, y) == 2
        assert gfx.scrn(5, 9) == 0
        assert gfx.scrn(5, 31) == 0

    def test_t01_08_color_negative(self):
        """T01-08 [Bloquant] COLOR= -1 declenche ILLEGAL QUANTITY ERROR."""
        gfx = GraphicsEngine()
        gfx.gr()
        e = _run_direct_err("COLOR= -1", gfx)
        assert e.code == 53

    def test_t01_09_color_overflow(self):
        """T01-09 [Bloquant] COLOR= 16 declenche ILLEGAL QUANTITY ERROR."""
        gfx = GraphicsEngine()
        gfx.gr()
        e = _run_direct_err("COLOR= 16", gfx)
        assert e.code == 53

    def test_t01_10_color_float_truncated(self):
        """T01-10 [Majeur] COLOR= 5.9 est tronqué à 5 (pas d'erreur)."""
        _, gfx = _run_program({10: "GR : COLOR= 5.9 : PLOT 0,0"})
        assert gfx.scrn(0, 0) == 5

    def test_t01_11_plot_x_oob(self):
        """T01-11 [Bloquant] PLOT 40,0 (x hors limites) declenche ILLEGAL QUANTITY ERROR."""
        gfx = GraphicsEngine()
        gfx.gr()
        e = _run_direct_err("PLOT 40,0", gfx)
        assert e.code == 53

    def test_t01_12_plot_y_oob(self):
        """T01-12 [Bloquant] PLOT 0,48 (y hors limites) declenche ILLEGAL QUANTITY ERROR."""
        gfx = GraphicsEngine()
        gfx.gr()
        e = _run_direct_err("PLOT 0,48", gfx)
        assert e.code == 53

    def test_t01_13_hlin_y_oob(self):
        """T01-13 [Bloquant] HLIN 0,39 AT 48 (y hors limites) declenche ILLEGAL QUANTITY ERROR."""
        gfx = GraphicsEngine()
        gfx.gr()
        e = _run_direct_err("HLIN 0,39 AT 48", gfx)
        assert e.code == 53

    def test_t01_14_vlin_x_oob(self):
        """T01-14 [Bloquant] VLIN 0,47 AT 40 (x hors limites) declenche ILLEGAL QUANTITY ERROR."""
        gfx = GraphicsEngine()
        gfx.gr()
        e = _run_direct_err("VLIN 0,47 AT 40", gfx)
        assert e.code == 53

    def test_t01_15_scrn_x_oob(self):
        """T01-15 [Bloquant] SCRN(40,0) (x hors limites) declenche ILLEGAL QUANTITY ERROR."""
        gfx = GraphicsEngine()
        gfx.gr()
        e = _run_direct_err("PRINT SCRN(40,0)", gfx)
        assert e.code == 53

    def test_t01_16_scrn_y_oob(self):
        """T01-16 [Bloquant] SCRN(0,48) (y hors limites) declenche ILLEGAL QUANTITY ERROR."""
        gfx = GraphicsEngine()
        gfx.gr()
        e = _run_direct_err("PRINT SCRN(0,48)", gfx)
        assert e.code == 53


# ============================================================
# UC-019 — Dessiner en haute résolution (T02-01 à T02-10)
# ============================================================


class TestUC019HiRes:
    """10 scénarios QA pour UC-019 : haute résolution."""

    def test_t02_01_hgr_page1(self):
        """T02-01 [Bloquant] HGR active la page 1, mode mixte, écran noir."""
        _, gfx = _run_direct("HGR")
        assert gfx.mode == "hires"
        assert gfx.hires_page == 1
        assert all(b == 0 for b in gfx.hires_buffer)

    def test_t02_02_hgr2_page2(self):
        """T02-02 [Bloquant] HGR2 active la page 2, plein écran, écran noir."""
        _, gfx = _run_direct("HGR2")
        assert gfx.mode == "hires"
        assert gfx.hires_page == 2
        assert all(b == 0 for b in gfx.hires_buffer)

    def test_t02_03_hplot_diagonal(self):
        """T02-03 [Bloquant] HCOLOR=1 : HPLOT 0,0 TO 279,191 trace une diagonale verte."""
        _, gfx = _run_program({10: "HGR : HCOLOR=1 : HPLOT 0,0 TO 279,191"})
        assert gfx.hires_pixel(0, 0) == 1
        assert gfx.hires_pixel(279, 191) == 1
        # Points intermédiaires doivent exister
        non_zero = sum(1 for b in gfx.hires_buffer if b != 0)
        assert non_zero > 2

    def test_t02_04_hplot_chained_square(self):
        """T02-04 [Bloquant] HPLOT enchaine trace un carre (segments enchaines)."""
        _, gfx = _run_program(
            {
                10: "HGR : HCOLOR=3 : HPLOT 0,0 TO 100,0 TO 100,100 TO 0,100 TO 0,0",
            }
        )
        # 4 coins
        assert gfx.hires_pixel(0, 0) == 3
        assert gfx.hires_pixel(100, 0) == 3
        assert gfx.hires_pixel(100, 100) == 3
        assert gfx.hires_pixel(0, 100) == 3
        # Points sur les arêtes
        assert gfx.hires_pixel(50, 0) == 3
        assert gfx.hires_pixel(100, 50) == 3
        assert gfx.hires_pixel(50, 100) == 3
        assert gfx.hires_pixel(0, 50) == 3

    def test_t02_05_hplot_to_from_last(self):
        """T02-05 [Bloquant] HPLOT 50,50 : HPLOT TO 100,100 dessine depuis derniere position."""
        _, gfx = _run_program(
            {
                10: "HGR : HCOLOR=3 : HPLOT 50,50",
                20: "HPLOT TO 100,100",
            }
        )
        assert gfx.hires_pixel(50, 50) == 3
        assert gfx.hires_pixel(100, 100) == 3

    def test_t02_06_hcolor_negative(self):
        """T02-06 [Bloquant] HCOLOR= -1 declenche ILLEGAL QUANTITY ERROR."""
        gfx = GraphicsEngine()
        gfx.hgr()
        e = _run_direct_err("HCOLOR= -1", gfx)
        assert e.code == 53

    def test_t02_07_hcolor_overflow(self):
        """T02-07 [Bloquant] HCOLOR= 8 declenche ILLEGAL QUANTITY ERROR."""
        gfx = GraphicsEngine()
        gfx.hgr()
        e = _run_direct_err("HCOLOR= 8", gfx)
        assert e.code == 53

    def test_t02_08_hplot_x_oob(self):
        """T02-08 [Bloquant] HPLOT 280,0 (x hors limites) declenche ILLEGAL QUANTITY ERROR."""
        gfx = GraphicsEngine()
        gfx.hgr()
        e = _run_direct_err("HPLOT 280,0", gfx)
        assert e.code == 53

    def test_t02_09_hplot_y_oob(self):
        """T02-09 [Bloquant] HPLOT 0,192 (y hors limites) declenche ILLEGAL QUANTITY ERROR."""
        gfx = GraphicsEngine()
        gfx.hgr()
        e = _run_direct_err("HPLOT 0,192", gfx)
        assert e.code == 53

    def test_t02_10_hplot_to_default_origin(self):
        """T02-10 [Majeur] HPLOT TO 50,50 sans HPLOT prealable trace depuis (0,0)."""
        _, gfx = _run_program({10: "HGR : HCOLOR=1 : HPLOT TO 10,10"})
        assert gfx.hires_pixel(0, 0) == 1
        assert gfx.hires_pixel(10, 10) == 1


# ============================================================
# UC-020 — Utiliser les shape tables (T03-01 à T03-09)
# ============================================================


class TestUC020ShapeTables:
    """9 scénarios QA pour UC-020 : shape tables."""

    def test_t03_01_draw_shape(self):
        """T03-01 [Bloquant] Shape table chargee + DRAW 1 AT 140,80 dessine la forme."""
        gfx = GraphicsEngine()
        gfx.hgr()
        gfx.set_hcolor(3)
        gfx.set_rot(0)
        gfx.set_scale(1)
        gfx.load_shape_table(_make_shape_table())
        gfx.draw_shape(1, 140, 80)
        drawn = any(
            gfx.hires_pixel(140 + dx, 80 + dy) != 0
            for dy in range(-5, 6)
            for dx in range(-5, 6)
            if 0 <= 140 + dx < 280 and 0 <= 80 + dy < 192
        )
        assert drawn, "DRAW devrait avoir dessine au moins un pixel"

    def test_t03_02_xdraw_erases(self):
        """T03-02 [Bloquant] DRAW puis XDRAW meme position efface la forme (XOR)."""
        gfx = GraphicsEngine()
        gfx.hgr()
        gfx.set_hcolor(3)
        gfx.set_rot(0)
        gfx.set_scale(1)
        gfx.load_shape_table(_make_shape_table())
        gfx.draw_shape(1, 140, 80)
        gfx.xdraw_shape(1, 140, 80)
        for dy in range(-5, 6):
            for dx in range(-5, 6):
                px, py = 140 + dx, 80 + dy
                if 0 <= px < 280 and 0 <= py < 192:
                    assert gfx.hires_pixel(px, py) == 0

    def test_t03_03_rot_and_scale(self):
        """T03-03 [Majeur] ROT=16 : SCALE=2 : DRAW 1 AT 140,80 applique rotation et echelle."""
        gfx = GraphicsEngine()
        gfx.hgr()
        gfx.set_hcolor(3)
        gfx.set_rot(16)
        gfx.set_scale(2)
        gfx.load_shape_table(_make_shape_table())
        gfx.draw_shape(1, 140, 80)
        drawn = any(
            gfx.hires_pixel(140 + dx, 80 + dy) != 0
            for dy in range(-10, 11)
            for dx in range(-10, 11)
            if 0 <= 140 + dx < 280 and 0 <= 80 + dy < 192
        )
        assert drawn, "DRAW avec ROT/SCALE devrait dessiner au moins un pixel"

    def test_t03_04_draw_no_table(self):
        """T03-04 [Bloquant] DRAW 1 AT 140,80 sans shape table declenche ILLEGAL QUANTITY ERROR."""
        gfx = GraphicsEngine()
        gfx.hgr()
        e = _run_direct_err("DRAW 1 AT 140,80", gfx)
        assert e.code == 53

    def test_t03_05_draw_zero(self):
        """T03-05 [Bloquant] DRAW 0 AT 140,80 (forme invalide) → ILLEGAL QUANTITY."""
        gfx = GraphicsEngine()
        gfx.hgr()
        gfx.load_shape_table(_make_shape_table())
        e = _run_direct_err("DRAW 0 AT 140,80", gfx)
        assert e.code == 53

    def test_t03_06_rot_negative(self):
        """T03-06 [Bloquant] ROT= -1 declenche ILLEGAL QUANTITY ERROR."""
        e = _run_direct_err("ROT= -1")
        assert e.code == 53

    def test_t03_07_rot_overflow(self):
        """T03-07 [Bloquant] ROT= 256 declenche ILLEGAL QUANTITY ERROR."""
        e = _run_direct_err("ROT= 256")
        assert e.code == 53

    def test_t03_08_scale_zero_invisible(self):
        """T03-08 [Majeur] SCALE= 0 rend la forme invisible (aucun pixel, pas d'erreur)."""
        gfx = GraphicsEngine()
        gfx.hgr()
        gfx.set_hcolor(3)
        gfx.set_rot(0)
        gfx.set_scale(0)
        gfx.load_shape_table(_make_shape_table())
        gfx.draw_shape(1, 140, 80)
        for dy in range(-5, 6):
            for dx in range(-5, 6):
                px, py = 140 + dx, 80 + dy
                if 0 <= px < 280 and 0 <= py < 192:
                    assert gfx.hires_pixel(px, py) == 0

    def test_t03_09_scale_overflow(self):
        """T03-09 [Bloquant] SCALE= 256 declenche ILLEGAL QUANTITY ERROR."""
        e = _run_direct_err("SCALE= 256")
        assert e.code == 53


# ============================================================
# UC-021 — Rendre les graphiques en terminal (T04-01 à T04-04)
# ============================================================


class TestUC021Rendering:
    """4 scénarios QA pour UC-021 : rendu terminal."""

    def test_t04_01_lores_render_ansi(self):
        """T04-01 [Majeur] Programme LoRes avec rectangle colore produit un rendu ANSI."""
        gfx = GraphicsEngine()
        gfx.gr()
        gfx.set_color(4)
        gfx.hlin(0, 39, 10)
        gfx.hlin(0, 39, 11)
        output = gfx.render_lores_ansi()
        assert len(output) > 0
        assert "\033[" in output  # Codes ANSI
        assert any(c in output for c in ("\u2580", "\u2584", "\u2588"))  # Blocs Unicode

    def test_t04_02_hires_render_ansi(self):
        """T04-02 [Majeur] Programme HiRes avec lignes produit un rendu ANSI."""
        gfx = GraphicsEngine()
        gfx.hgr()
        gfx.set_hcolor(1)
        gfx.hplot_line(0, 0, 279, 191)
        output = gfx.render_hires_ansi()
        assert len(output) > 0
        assert "\033[" in output
        assert any(c in output for c in ("\u2580", "\u2584", "\u2588"))

    def test_t04_03_lores_render_blank(self):
        """T04-03 [Mineur] Rendu LoRes ecran vierge (noir) ne contient que des blocs noirs."""
        gfx = GraphicsEngine()
        gfx.gr()
        output = gfx.render_lores_ansi()
        assert len(output) > 0
        # Le buffer est entierement noir
        for y in range(48):
            for x in range(40):
                assert gfx.scrn(x, y) == 0
        # Le rendu contient la couleur noire (0,0,0)
        assert "\033[38;2;0;0;0m" in output

    def test_t04_04_hires_render_blank(self):
        """T04-04 [Mineur] Rendu HiRes ecran vierge (noir) ne contient que des blocs noirs."""
        gfx = GraphicsEngine()
        gfx.hgr()
        output = gfx.render_hires_ansi()
        assert len(output) > 0
        # Le buffer est entierement noir
        assert all(b == 0 for b in gfx.hires_buffer)
        # Le rendu contient la couleur noire (0,0,0)
        assert "\033[38;2;0;0;0m" in output


# ============================================================
# Exigences non fonctionnelles et sécurité (T05-01 à T05-05)
# ============================================================


class TestT05NonFunctional:
    """5 scénarios QA pour ENF-001, ENF-005, SEC-DEV-01, SEC-DEV-02, SEC-DEV-05."""

    def test_t05_01_no_forbidden_imports(self):
        """T05-01 [Bloquant] graphics.py n'importe aucun module interdit."""
        import applesoft.graphics as gmod

        source = inspect.getsource(gmod)
        forbidden = ["ctypes", "numpy", "threading", "multiprocessing", "subprocess"]
        for mod in forbidden:
            assert f"import {mod}" not in source, f"Module interdit trouve : {mod}"

    def test_t05_02_graphics_engine_isolated(self):
        """T05-02 [Majeur] GraphicsEngine est instanciable et testable sans IOBridge."""
        gfx = GraphicsEngine()
        # Doit fonctionner sans aucun callback configure
        gfx.gr()
        gfx.set_color(1)
        gfx.plot(5, 5)
        assert gfx.scrn(5, 5) == 1

        gfx.hgr()
        gfx.set_hcolor(1)
        gfx.hplot_point(10, 10)
        assert gfx.hires_pixel(10, 10) == 1

        # Le rendu fonctionne aussi sans callback
        render = gfx.render_hires_ansi()
        assert len(render) > 0

    def test_t05_03_no_eval_exec(self):
        """T05-03 [Bloquant] graphics.py ne contient aucun eval/exec/pickle/compile."""
        import applesoft.graphics as gmod

        source = inspect.getsource(gmod)
        assert "eval(" not in source, "eval() trouve dans graphics.py"
        assert "exec(" not in source, "exec() trouve dans graphics.py"
        assert "pickle" not in source, "pickle trouve dans graphics.py"
        assert "compile(" not in source, "compile() trouve dans graphics.py"

    def test_t05_04_fail_securely(self):
        """T05-04 [Bloquant] Erreur de bornes dans GraphicsEngine leve ValueError
        convertie en BasicError(53) par l'Interpreter (fail securely)."""
        # 1. GraphicsEngine leve ValueError directement
        gfx = GraphicsEngine()
        gfx.gr()
        with pytest.raises(ValueError):
            gfx.plot(40, 0)
        with pytest.raises(ValueError):
            gfx.scrn(0, 48)
        with pytest.raises(ValueError):
            gfx.set_color(-1)

        # 2. L'Interpreter convertit en BasicError(53)
        gfx2 = GraphicsEngine()
        gfx2.gr()
        e = _run_direct_err("PLOT 40,0", gfx2)
        assert e.code == 53

        gfx3 = GraphicsEngine()
        gfx3.hgr()
        e2 = _run_direct_err("HPLOT 280,0", gfx3)
        assert e2.code == 53

    def test_t05_05_buffers_bounded(self):
        """T05-05 [Majeur] Les buffers LoRes (40x48) et HiRes (280x192) sont de taille fixe."""
        gfx = GraphicsEngine()

        # LoRes : 40 * 48 = 1920
        gfx.gr()
        assert len(gfx.lores_buffer) == 40 * 48
        assert isinstance(gfx.lores_buffer, bytearray)

        # HiRes : 280 * 192 = 53760
        gfx.hgr()
        assert len(gfx.hires_buffer) == 280 * 192
        assert isinstance(gfx.hires_buffer, bytearray)

        # Les buffers ne sont pas extensibles via des methodes publiques
        assert not hasattr(gfx, "resize_lores_buffer")
        assert not hasattr(gfx, "resize_hires_buffer")
