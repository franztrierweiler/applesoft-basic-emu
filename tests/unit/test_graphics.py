"""Tests unitaires pour le moteur graphique (UC-018, UC-019, UC-020, UC-021)."""

from __future__ import annotations

import pytest

from applesoft.graphics import GraphicsEngine

# === F1 — Basse résolution (UC-018) ===


class TestLoResMode:
    """Tests du mode basse résolution."""

    def test_ca_uc_018_01_gr_active_lores(self):
        """CA-UC-018-01 : GR → mode LoRes activé, écran noir."""
        gfx = GraphicsEngine()
        gfx.gr()
        assert gfx.mode == "lores"
        # Buffer 40x48 entièrement noir (couleur 0)
        for y in range(48):
            for x in range(40):
                assert gfx.scrn(x, y) == 0

    def test_ca_uc_018_02_plot_magenta(self):
        """CA-UC-018-02 : GR : COLOR=1 : PLOT 5,5 → bloc magenta en (5,5)."""
        gfx = GraphicsEngine()
        gfx.gr()
        gfx.set_color(1)
        gfx.plot(5, 5)
        assert gfx.scrn(5, 5) == 1

    def test_ca_uc_018_03_hlin_green(self):
        """CA-UC-018-03 : COLOR=4 : HLIN 0,39 AT 20 → ligne horizontale."""
        gfx = GraphicsEngine()
        gfx.gr()
        gfx.set_color(4)
        gfx.hlin(0, 39, 20)
        for x in range(40):
            assert gfx.scrn(x, 20) == 4

    def test_ca_uc_018_04_hlin_inverted_bounds(self):
        """CA-UC-018-04 : HLIN 30,10 AT 5 → inversion des bornes."""
        gfx = GraphicsEngine()
        gfx.gr()
        gfx.set_color(1)
        gfx.hlin(30, 10, 5)
        for x in range(10, 31):
            assert gfx.scrn(x, 5) == 1
        # En dehors de la plage
        assert gfx.scrn(9, 5) == 0
        assert gfx.scrn(31, 5) == 0

    def test_ca_uc_018_05_scrn_reads_color(self):
        """CA-UC-018-05 : COLOR=9 : PLOT 5,5 : SCRN(5,5) → 9."""
        gfx = GraphicsEngine()
        gfx.gr()
        gfx.set_color(9)
        gfx.plot(5, 5)
        assert gfx.scrn(5, 5) == 9

    def test_ca_uc_018_06_text_restores_text_mode(self):
        """CA-UC-018-06 : TEXT → mode texte restauré."""
        gfx = GraphicsEngine()
        gfx.gr()
        assert gfx.mode == "lores"
        gfx.text()
        assert gfx.mode == "text"

    def test_vlin(self):
        """VLIN y1,y2 AT x → ligne verticale."""
        gfx = GraphicsEngine()
        gfx.gr()
        gfx.set_color(3)
        gfx.vlin(0, 47, 20)
        for y in range(48):
            assert gfx.scrn(20, y) == 3

    def test_vlin_inverted_bounds(self):
        """VLIN 30,10 AT 5 → inversion des bornes."""
        gfx = GraphicsEngine()
        gfx.gr()
        gfx.set_color(2)
        gfx.vlin(30, 10, 5)
        for y in range(10, 31):
            assert gfx.scrn(5, y) == 2
        assert gfx.scrn(5, 9) == 0
        assert gfx.scrn(5, 31) == 0

    def test_color_truncates_float(self):
        """COLOR= avec flottant → tronqué."""
        gfx = GraphicsEngine()
        gfx.gr()
        gfx.set_color(5)  # 5.9 tronqué à 5 par l'interpréteur
        gfx.plot(0, 0)
        assert gfx.scrn(0, 0) == 5

    def test_plot_out_of_bounds_x(self):
        """PLOT 40,0 → erreur."""
        gfx = GraphicsEngine()
        gfx.gr()
        with pytest.raises(ValueError, match="x"):
            gfx.plot(40, 0)

    def test_plot_out_of_bounds_y(self):
        """PLOT 0,48 → erreur."""
        gfx = GraphicsEngine()
        gfx.gr()
        with pytest.raises(ValueError, match="y"):
            gfx.plot(0, 48)

    def test_hlin_out_of_bounds(self):
        """HLIN 0,39 AT 48 → erreur."""
        gfx = GraphicsEngine()
        gfx.gr()
        with pytest.raises(ValueError):
            gfx.hlin(0, 39, 48)

    def test_vlin_out_of_bounds(self):
        """VLIN 0,47 AT 40 → erreur."""
        gfx = GraphicsEngine()
        gfx.gr()
        with pytest.raises(ValueError):
            gfx.vlin(0, 47, 40)

    def test_scrn_out_of_bounds(self):
        """SCRN(40,0) → erreur."""
        gfx = GraphicsEngine()
        gfx.gr()
        with pytest.raises(ValueError):
            gfx.scrn(40, 0)

    def test_color_out_of_range_negative(self):
        """COLOR= -1 → erreur."""
        gfx = GraphicsEngine()
        gfx.gr()
        with pytest.raises(ValueError):
            gfx.set_color(-1)

    def test_color_out_of_range_high(self):
        """COLOR= 16 → erreur."""
        gfx = GraphicsEngine()
        gfx.gr()
        with pytest.raises(ValueError):
            gfx.set_color(16)


# === F2 — Haute résolution (UC-019) ===


class TestHiResMode:
    """Tests du mode haute résolution."""

    def test_ca_uc_019_01_hgr_activates_page1(self):
        """CA-UC-019-01 : HGR → page 1, mode mixte, écran noir."""
        gfx = GraphicsEngine()
        gfx.hgr()
        assert gfx.mode == "hires"
        assert gfx.hires_page == 1
        # Buffer noir
        assert all(b == 0 for b in gfx.hires_buffer)

    def test_ca_uc_019_02_hgr2_activates_page2(self):
        """CA-UC-019-02 : HGR2 → page 2, plein écran."""
        gfx = GraphicsEngine()
        gfx.hgr2()
        assert gfx.mode == "hires"
        assert gfx.hires_page == 2

    def test_ca_uc_019_03_hplot_diagonal(self):
        """CA-UC-019-03 : HCOLOR=1 : HPLOT 0,0 TO 279,191 → diagonale."""
        gfx = GraphicsEngine()
        gfx.hgr()
        gfx.set_hcolor(1)
        gfx.hplot_line(0, 0, 279, 191)
        # Les points de début et de fin doivent être dessinés
        assert gfx.hires_pixel(0, 0) == 1
        assert gfx.hires_pixel(279, 191) == 1

    def test_ca_uc_019_04_hplot_chained_square(self):
        """CA-UC-019-04 : HPLOT enchaîné → carré tracé."""
        gfx = GraphicsEngine()
        gfx.hgr()
        gfx.set_hcolor(3)
        # Carré : (0,0) → (100,0) → (100,100) → (0,100) → (0,0)
        gfx.hplot_point(0, 0)
        gfx.hplot_line(0, 0, 100, 0)
        gfx.hplot_line(100, 0, 100, 100)
        gfx.hplot_line(100, 100, 0, 100)
        gfx.hplot_line(0, 100, 0, 0)
        # Vérifier les 4 coins
        assert gfx.hires_pixel(0, 0) == 3
        assert gfx.hires_pixel(100, 0) == 3
        assert gfx.hires_pixel(100, 100) == 3
        assert gfx.hires_pixel(0, 100) == 3

    def test_ca_uc_019_05_hplot_point_and_line_from_last(self):
        """CA-UC-019-05 : HPLOT 50,50 : HPLOT TO 100,100."""
        gfx = GraphicsEngine()
        gfx.hgr()
        gfx.set_hcolor(3)
        gfx.hplot_point(50, 50)
        assert gfx.last_hplot_x == 50
        assert gfx.last_hplot_y == 50
        gfx.hplot_to(100, 100)
        assert gfx.hires_pixel(50, 50) == 3
        assert gfx.hires_pixel(100, 100) == 3

    def test_hplot_to_default_origin(self):
        """HPLOT TO sans HPLOT préalable → dernière position = (0,0)."""
        gfx = GraphicsEngine()
        gfx.hgr()
        gfx.set_hcolor(1)
        assert gfx.last_hplot_x == 0
        assert gfx.last_hplot_y == 0
        gfx.hplot_to(10, 10)
        assert gfx.hires_pixel(0, 0) == 1
        assert gfx.hires_pixel(10, 10) == 1

    def test_hcolor_out_of_range(self):
        """HCOLOR= -1 ou 8 → erreur."""
        gfx = GraphicsEngine()
        gfx.hgr()
        with pytest.raises(ValueError):
            gfx.set_hcolor(-1)
        with pytest.raises(ValueError):
            gfx.set_hcolor(8)

    def test_hplot_out_of_bounds_x(self):
        """HPLOT 280,0 → erreur."""
        gfx = GraphicsEngine()
        gfx.hgr()
        with pytest.raises(ValueError):
            gfx.hplot_point(280, 0)

    def test_hplot_out_of_bounds_y(self):
        """HPLOT 0,192 → erreur."""
        gfx = GraphicsEngine()
        gfx.hgr()
        with pytest.raises(ValueError):
            gfx.hplot_point(0, 192)


# === F3 — Shape tables (UC-020) ===


class TestShapeTables:
    """Tests des shape tables."""

    def _make_simple_shape_table(self) -> bytes:
        """Crée une shape table minimale avec une forme simple (un pixel vers le haut)."""
        # Format Apple II shape table :
        # - 2 octets : nombre de formes (little-endian)
        # - Pour chaque forme : 2 octets offset (little-endian)
        # - Données de la forme : octets de vecteurs, terminé par 0x00
        #
        # Chaque octet contient 3 vecteurs (bits 0-1, 2-4, 5-7):
        # Bits 0-1 du vecteur : 00=haut, 01=droite, 10=bas, 11=gauche
        # Bit de plot : 1 = tracer, 0 = déplacer sans tracer
        #
        # Un vecteur se compose de : bit_plot (1 bit) + direction (2 bits)
        # Pour le premier vecteur (bits 0-2) : bit0 = plot, bits 1-2 = direction
        # Forme simple : un point vers le haut avec plot
        # Vecteur : plot=1, direction=haut(00) → bits = 001 = 0x01
        # puis fin → 0x00
        num_shapes = 1
        # Offset de la forme 1 : après header (2 + 2*num_shapes = 4)
        offset = 4
        header = bytes(
            [
                num_shapes & 0xFF,
                (num_shapes >> 8) & 0xFF,
                offset & 0xFF,
                (offset >> 8) & 0xFF,
            ]
        )
        # Forme : un vecteur plot+haut, puis fin
        # Bits 0-2 : vecteur A (plot=1, dir=00=haut) → 001 = 1
        # Bits 3-5 : pas de vecteur B → 000
        # Bits 6-7 : pas de vecteur C → 00
        shape_data = bytes([0x01, 0x00])
        return header + shape_data

    def test_ca_uc_020_01_draw_shape(self):
        """CA-UC-020-01 : Shape table chargée + DRAW → forme dessinée."""
        gfx = GraphicsEngine()
        gfx.hgr()
        gfx.set_hcolor(3)
        gfx.set_rot(0)
        gfx.set_scale(1)
        shape_data = self._make_simple_shape_table()
        gfx.load_shape_table(shape_data)
        gfx.draw_shape(1, 140, 80)
        # Au moins un pixel dessiné autour de (140, 80)
        drawn = False
        for dy in range(-5, 6):
            for dx in range(-5, 6):
                px, py = 140 + dx, 80 + dy
                if 0 <= px < 280 and 0 <= py < 192:
                    if gfx.hires_pixel(px, py) != 0:
                        drawn = True
                        break
        assert drawn, "DRAW devrait avoir dessiné au moins un pixel"

    def test_ca_uc_020_02_xdraw_erases(self):
        """CA-UC-020-02 : DRAW puis XDRAW même position → forme effacée."""
        gfx = GraphicsEngine()
        gfx.hgr()
        gfx.set_hcolor(3)
        gfx.set_rot(0)
        gfx.set_scale(1)
        shape_data = self._make_simple_shape_table()
        gfx.load_shape_table(shape_data)
        gfx.draw_shape(1, 140, 80)
        gfx.xdraw_shape(1, 140, 80)
        # Tous les pixels autour de (140, 80) doivent être à 0 (effacés par XOR)
        for dy in range(-5, 6):
            for dx in range(-5, 6):
                px, py = 140 + dx, 80 + dy
                if 0 <= px < 280 and 0 <= py < 192:
                    assert gfx.hires_pixel(px, py) == 0

    def test_ca_uc_020_03_rot_and_scale(self):
        """CA-UC-020-03 : ROT=16, SCALE=2 → rotation 90° et échelle 2."""
        gfx = GraphicsEngine()
        gfx.hgr()
        gfx.set_hcolor(3)
        gfx.set_rot(16)
        gfx.set_scale(2)
        shape_data = self._make_simple_shape_table()
        gfx.load_shape_table(shape_data)
        gfx.draw_shape(1, 140, 80)
        # Avec rotation 90° et échelle 2, les pixels sont déplacés
        drawn = False
        for dy in range(-10, 11):
            for dx in range(-10, 11):
                px, py = 140 + dx, 80 + dy
                if 0 <= px < 280 and 0 <= py < 192:
                    if gfx.hires_pixel(px, py) != 0:
                        drawn = True
                        break
        assert drawn, "DRAW avec ROT/SCALE devrait avoir dessiné au moins un pixel"

    def test_draw_without_shape_table(self):
        """DRAW sans shape table chargée → erreur."""
        gfx = GraphicsEngine()
        gfx.hgr()
        with pytest.raises(ValueError, match="shape"):
            gfx.draw_shape(1, 140, 80)

    def test_draw_shape_zero(self):
        """DRAW 0 → erreur (forme 0 invalide)."""
        gfx = GraphicsEngine()
        gfx.hgr()
        shape_data = self._make_simple_shape_table()
        gfx.load_shape_table(shape_data)
        with pytest.raises(ValueError):
            gfx.draw_shape(0, 140, 80)

    def test_scale_zero_invisible(self):
        """SCALE= 0 → forme invisible (pas de pixel)."""
        gfx = GraphicsEngine()
        gfx.hgr()
        gfx.set_hcolor(3)
        gfx.set_rot(0)
        gfx.set_scale(0)
        shape_data = self._make_simple_shape_table()
        gfx.load_shape_table(shape_data)
        gfx.draw_shape(1, 140, 80)
        # Aucun pixel ne doit être dessiné
        for dy in range(-5, 6):
            for dx in range(-5, 6):
                px, py = 140 + dx, 80 + dy
                if 0 <= px < 280 and 0 <= py < 192:
                    assert gfx.hires_pixel(px, py) == 0

    def test_rot_out_of_range(self):
        """ROT= -1 ou 256 → erreur."""
        gfx = GraphicsEngine()
        with pytest.raises(ValueError):
            gfx.set_rot(-1)
        with pytest.raises(ValueError):
            gfx.set_rot(256)

    def test_scale_out_of_range(self):
        """SCALE= 256 → erreur."""
        gfx = GraphicsEngine()
        with pytest.raises(ValueError):
            gfx.set_scale(256)


# === F4 — Rendu CLI (UC-021) ===


class TestCliRendering:
    """Tests du rendu terminal."""

    def test_ca_uc_021_01_lores_render(self):
        """CA-UC-021-01 : Programme LoRes → rendu visible."""
        gfx = GraphicsEngine()
        gfx.gr()
        gfx.set_color(4)
        gfx.hlin(0, 39, 10)
        gfx.hlin(0, 39, 11)
        output = gfx.render_lores_ansi()
        assert len(output) > 0
        # Doit contenir des codes ANSI de couleur
        assert "\033[" in output

    def test_ca_uc_021_02_hires_render(self):
        """CA-UC-021-02 : Programme HiRes → rendu visible."""
        gfx = GraphicsEngine()
        gfx.hgr()
        gfx.set_hcolor(1)
        gfx.hplot_line(0, 0, 279, 191)
        output = gfx.render_hires_ansi()
        assert len(output) > 0
        assert "\033[" in output
