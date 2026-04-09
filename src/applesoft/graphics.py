"""Moteur graphique Applesoft BASIC (UC-018, UC-019, UC-020, UC-021).

Gère les buffers LoRes (40x48, 16 couleurs) et HiRes (280x192, 8 couleurs),
l'état graphique (mode, couleur, position, ROT, SCALE), la logique de dessin
(PLOT, HPLOT, HLIN, VLIN, DRAW/XDRAW, SCRN), et le rendu CLI (ANSI + Unicode).
"""

from __future__ import annotations

import math

# Palette Apple II LoRes — 16 couleurs (index → RGB)
LORES_PALETTE: list[tuple[int, int, int]] = [
    (0, 0, 0),  # 0 — noir
    (227, 30, 96),  # 1 — magenta
    (96, 78, 189),  # 2 — bleu foncé
    (255, 68, 253),  # 3 — violet
    (0, 163, 96),  # 4 — vert foncé
    (156, 156, 156),  # 5 — gris 1
    (20, 207, 253),  # 6 — bleu moyen
    (208, 195, 255),  # 7 — bleu clair
    (96, 114, 3),  # 8 — brun
    (255, 106, 60),  # 9 — orange
    (156, 156, 156),  # 10 — gris 2
    (255, 160, 208),  # 11 — rose
    (20, 245, 60),  # 12 — vert clair
    (208, 221, 141),  # 13 — jaune
    (114, 255, 208),  # 14 — aqua
    (255, 255, 255),  # 15 — blanc
]

# Palette Apple II HiRes — 8 couleurs
HIRES_PALETTE: list[tuple[int, int, int]] = [
    (0, 0, 0),  # 0 — noir 1
    (0, 163, 96),  # 1 — vert
    (255, 68, 253),  # 2 — violet
    (255, 255, 255),  # 3 — blanc 1
    (0, 0, 0),  # 4 — noir 2
    (255, 106, 60),  # 5 — orange
    (20, 207, 253),  # 6 — bleu
    (255, 255, 255),  # 7 — blanc 2
]


class GraphicsEngine:
    """Moteur graphique Apple II."""

    # Dimensions
    LORES_WIDTH = 40
    LORES_HEIGHT = 48
    HIRES_WIDTH = 280
    HIRES_HEIGHT = 192

    def __init__(self):
        self._mode: str = "text"  # "text", "lores", "hires"
        self._lores_color: int = 0
        self._hires_color: int = 0
        self._hires_page: int = 1
        self._rot: int = 0
        self._scale: int = 1
        self._last_hplot_x: int = 0
        self._last_hplot_y: int = 0
        self._shape_table: bytes | None = None
        # Buffers
        self._lores_buffer = bytearray(self.LORES_WIDTH * self.LORES_HEIGHT)
        self._hires_buffer = bytearray(self.HIRES_WIDTH * self.HIRES_HEIGHT)
        # Callback de rendu (branché par IOBridgeCLI)
        self._on_draw: callable | None = None
        self._dirty: bool = False

    # --- Propriétés ---

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def hires_page(self) -> int:
        return self._hires_page

    @property
    def hires_buffer(self) -> bytearray:
        return self._hires_buffer

    @property
    def lores_buffer(self) -> bytearray:
        return self._lores_buffer

    @property
    def last_hplot_x(self) -> int:
        return self._last_hplot_x

    @property
    def last_hplot_y(self) -> int:
        return self._last_hplot_y

    @property
    def dirty(self) -> bool:
        return self._dirty

    def set_on_draw(self, callback: callable) -> None:
        """Installe le callback de rendu temps réel."""
        self._on_draw = callback

    def _notify_draw(self) -> None:
        """Signale une modification pour le rendu temps réel."""
        self._dirty = True
        if self._on_draw is not None:
            self._on_draw()

    # === Basse résolution (UC-018) ===

    def gr(self) -> None:
        """Active le mode LoRes 40x48, écran noir, couleur 0."""
        self._mode = "lores"
        self._lores_color = 0
        self._lores_buffer = bytearray(self.LORES_WIDTH * self.LORES_HEIGHT)
        self._notify_draw()

    def set_color(self, n: int) -> None:
        """COLOR= n (0-15)."""
        if n < 0 or n > 15:
            raise ValueError(f"COLOR= {n} : valeur hors limites (0-15)")
        self._lores_color = n

    def plot(self, x: int, y: int) -> None:
        """PLOT x,y — dessine un bloc LoRes."""
        self._check_lores_bounds(x, y)
        self._lores_buffer[y * self.LORES_WIDTH + x] = self._lores_color
        self._notify_draw()

    def hlin(self, x1: int, x2: int, y: int) -> None:
        """HLIN x1,x2 AT y — ligne horizontale LoRes."""
        if x1 > x2:
            x1, x2 = x2, x1
        self._check_lores_bounds(x1, y)
        self._check_lores_bounds(x2, y)
        for x in range(x1, x2 + 1):
            self._lores_buffer[y * self.LORES_WIDTH + x] = self._lores_color
        self._notify_draw()

    def vlin(self, y1: int, y2: int, x: int) -> None:
        """VLIN y1,y2 AT x — ligne verticale LoRes."""
        if y1 > y2:
            y1, y2 = y2, y1
        self._check_lores_bounds(x, y1)
        self._check_lores_bounds(x, y2)
        for y in range(y1, y2 + 1):
            self._lores_buffer[y * self.LORES_WIDTH + x] = self._lores_color
        self._notify_draw()

    def scrn(self, x: int, y: int) -> int:
        """SCRN(x,y) — retourne le code couleur du bloc LoRes."""
        self._check_lores_bounds(x, y)
        return self._lores_buffer[y * self.LORES_WIDTH + x]

    def text(self) -> None:
        """TEXT — retour au mode texte."""
        self._mode = "text"

    def _check_lores_bounds(self, x: int, y: int) -> None:
        """Vérifie les bornes LoRes."""
        if x < 0 or x >= self.LORES_WIDTH:
            raise ValueError(f"x={x} hors limites (0-{self.LORES_WIDTH - 1})")
        if y < 0 or y >= self.LORES_HEIGHT:
            raise ValueError(f"y={y} hors limites (0-{self.LORES_HEIGHT - 1})")

    # === Haute résolution (UC-019) ===

    def hgr(self) -> None:
        """HGR — page 1, mode mixte, écran noir."""
        self._mode = "hires"
        self._hires_page = 1
        self._hires_color = 0
        self._last_hplot_x = 0
        self._last_hplot_y = 0
        self._hires_buffer = bytearray(self.HIRES_WIDTH * self.HIRES_HEIGHT)
        self._notify_draw()

    def hgr2(self) -> None:
        """HGR2 — page 2, plein écran, écran noir."""
        self._mode = "hires"
        self._hires_page = 2
        self._hires_color = 0
        self._last_hplot_x = 0
        self._last_hplot_y = 0
        self._hires_buffer = bytearray(self.HIRES_WIDTH * self.HIRES_HEIGHT)
        self._notify_draw()

    def set_hcolor(self, n: int) -> None:
        """HCOLOR= n (0-7)."""
        if n < 0 or n > 7:
            raise ValueError(f"HCOLOR= {n} : valeur hors limites (0-7)")
        self._hires_color = n

    def hplot_point(self, x: int, y: int) -> None:
        """HPLOT x,y — dessine un point HiRes."""
        self._check_hires_bounds(x, y)
        self._hires_buffer[y * self.HIRES_WIDTH + x] = self._hires_color
        self._last_hplot_x = x
        self._last_hplot_y = y
        self._notify_draw()

    def hplot_line(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """HPLOT x1,y1 TO x2,y2 — ligne HiRes (algorithme de Bresenham)."""
        self._check_hires_bounds(x1, y1)
        self._check_hires_bounds(x2, y2)
        self._bresenham(x1, y1, x2, y2, self._hires_color)
        self._last_hplot_x = x2
        self._last_hplot_y = y2
        self._notify_draw()

    def hplot_to(self, x: int, y: int) -> None:
        """HPLOT TO x,y — depuis la dernière position."""
        self.hplot_line(self._last_hplot_x, self._last_hplot_y, x, y)

    def hires_pixel(self, x: int, y: int) -> int:
        """Lit un pixel HiRes (pour les tests)."""
        self._check_hires_bounds(x, y)
        return self._hires_buffer[y * self.HIRES_WIDTH + x]

    def _check_hires_bounds(self, x: int, y: int) -> None:
        """Vérifie les bornes HiRes."""
        if x < 0 or x >= self.HIRES_WIDTH:
            raise ValueError(f"x={x} hors limites (0-{self.HIRES_WIDTH - 1})")
        if y < 0 or y >= self.HIRES_HEIGHT:
            raise ValueError(f"y={y} hors limites (0-{self.HIRES_HEIGHT - 1})")

    def _bresenham(self, x0: int, y0: int, x1: int, y1: int, color: int) -> None:
        """Algorithme de Bresenham pour tracer une ligne."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy

        while True:
            self._hires_buffer[y0 * self.HIRES_WIDTH + x0] = color
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    # === Shape tables (UC-020) ===

    def set_rot(self, n: int) -> None:
        """ROT= n (0-255)."""
        if n < 0 or n > 255:
            raise ValueError(f"ROT= {n} : valeur hors limites (0-255)")
        self._rot = n

    def set_scale(self, n: int) -> None:
        """SCALE= n (0-255)."""
        if n < 0 or n > 255:
            raise ValueError(f"SCALE= {n} : valeur hors limites (0-255)")
        self._scale = n

    def load_shape_table(self, data: bytes) -> None:
        """Charge une shape table depuis des données binaires."""
        self._shape_table = data

    def draw_shape(self, shape_num: int, x: int, y: int) -> None:
        """DRAW n AT x,y — dessine une forme."""
        self._render_shape(shape_num, x, y, xor=False)

    def xdraw_shape(self, shape_num: int, x: int, y: int) -> None:
        """XDRAW n AT x,y — dessine une forme en XOR."""
        self._render_shape(shape_num, x, y, xor=True)

    def _render_shape(self, shape_num: int, cx: int, cy: int, *, xor: bool) -> None:
        """Rendu d'une forme depuis la shape table."""
        if self._shape_table is None:
            raise ValueError("Pas de shape table chargée")
        if shape_num < 1:
            raise ValueError(f"Forme {shape_num} invalide (doit être >= 1)")

        # Lire le header de la shape table
        if len(self._shape_table) < 2:
            raise ValueError("Shape table trop courte")
        num_shapes = self._shape_table[0] | (self._shape_table[1] << 8)
        if shape_num > num_shapes:
            raise ValueError(f"Forme {shape_num} > {num_shapes} formes disponibles")

        # Lire l'offset de la forme
        offset_idx = 2 + (shape_num - 1) * 2
        if offset_idx + 1 >= len(self._shape_table):
            raise ValueError("Shape table corrompue")
        shape_offset = self._shape_table[offset_idx] | (self._shape_table[offset_idx + 1] << 8)

        # SCALE=0 → invisible
        if self._scale == 0:
            return

        # Décoder et rendre la forme
        rot_rad = self._rot * math.pi * 2.0 / 64.0
        cos_r = math.cos(rot_rad)
        sin_r = math.sin(rot_rad)
        scale = self._scale

        # Position courante en coordonnées fractionnaires
        fx, fy = 0.0, 0.0
        pos = shape_offset

        while pos < len(self._shape_table):
            byte = self._shape_table[pos]
            if byte == 0:
                break
            pos += 1

            # Décoder les 3 vecteurs du byte
            # Vecteur A : bits 0-2 (bit 0 = plot, bits 1-2 = direction)
            # Vecteur B : bits 3-5 (bit 3 = plot, bits 4-5 = direction)
            # Vecteur C : bits 6-7 (direction uniquement, toujours plot)
            vectors = []

            # Vecteur A
            plot_a = (byte >> 0) & 1
            dir_a = (byte >> 1) & 3
            vectors.append((plot_a, dir_a))

            # Vecteur B (seulement si non nul)
            b_bits = (byte >> 3) & 7
            if b_bits != 0:
                plot_b = (byte >> 3) & 1
                dir_b = (byte >> 4) & 3
                vectors.append((plot_b, dir_b))

                # Vecteur C (seulement si non nul et B existe)
                c_bits = (byte >> 6) & 3
                if c_bits != 0:
                    dir_c = (byte >> 6) & 3
                    vectors.append((1, dir_c))  # C toujours plot

            for plot, direction in vectors:
                # Direction de base : 0=haut, 1=droite, 2=bas, 3=gauche
                if direction == 0:
                    ddx, ddy = 0.0, -1.0
                elif direction == 1:
                    ddx, ddy = 1.0, 0.0
                elif direction == 2:
                    ddx, ddy = 0.0, 1.0
                else:
                    ddx, ddy = -1.0, 0.0

                # Appliquer rotation
                rdx = ddx * cos_r - ddy * sin_r
                rdy = ddx * sin_r + ddy * cos_r

                # Appliquer échelle
                fx += rdx * scale
                fy += rdy * scale

                # Dessiner si plot
                if plot:
                    px = cx + int(round(fx))
                    py = cy + int(round(fy))
                    if 0 <= px < self.HIRES_WIDTH and 0 <= py < self.HIRES_HEIGHT:
                        idx = py * self.HIRES_WIDTH + px
                        if xor:
                            if self._hires_buffer[idx] != 0:
                                self._hires_buffer[idx] = 0
                            else:
                                self._hires_buffer[idx] = self._hires_color
                        else:
                            self._hires_buffer[idx] = self._hires_color

        self._notify_draw()

    # === Rendu CLI (UC-021) ===

    def render_lores_ansi(self) -> str:
        """Rendu LoRes en ANSI + Unicode blocs (▀▄█).

        Utilise des demi-blocs : chaque caractère représente 2 lignes verticales.
        ▀ = couleur du haut, ▄ = couleur du bas, █ = les deux identiques.
        """
        lines = []
        for row in range(0, self.LORES_HEIGHT, 2):
            line_parts = []
            for col in range(self.LORES_WIDTH):
                top = self._lores_buffer[row * self.LORES_WIDTH + col]
                if row + 1 < self.LORES_HEIGHT:
                    bottom = self._lores_buffer[(row + 1) * self.LORES_WIDTH + col]
                else:
                    bottom = 0
                r_top, g_top, b_top = LORES_PALETTE[top]
                r_bot, g_bot, b_bot = LORES_PALETTE[bottom]

                if top == bottom:
                    # Les deux moitiés identiques → bloc plein
                    line_parts.append(f"\033[38;2;{r_top};{g_top};{b_top}m█")
                else:
                    # Demi-bloc : fg = haut (▀), bg = bas
                    line_parts.append(
                        f"\033[38;2;{r_top};{g_top};{b_top};48;2;{r_bot};{g_bot};{b_bot}m▀"
                    )
            lines.append("".join(line_parts) + "\033[0m")
        return "\n".join(lines)

    def render_hires_ansi(self, max_width: int = 140, max_height: int = 48) -> str:
        """Rendu HiRes en ANSI + Unicode (best effort, downscale).

        Le rendu est approximatif : le terminal ne peut pas afficher 280x192 pixels.
        On downscale vers max_width x max_height avec demi-blocs.
        """
        # Facteur de réduction
        sx = max(1, self.HIRES_WIDTH // max_width)
        sy = max(1, self.HIRES_HEIGHT // (max_height * 2))  # *2 car demi-blocs

        out_w = self.HIRES_WIDTH // sx
        out_h = self.HIRES_HEIGHT // sy

        # Downscale : moyenne de la zone
        scaled = []
        for y in range(out_h):
            row = []
            for x in range(out_w):
                total = 0
                count = 0
                for dy in range(sy):
                    for dx in range(sx):
                        src_x = x * sx + dx
                        src_y = y * sy + dy
                        if src_x < self.HIRES_WIDTH and src_y < self.HIRES_HEIGHT:
                            c = self._hires_buffer[src_y * self.HIRES_WIDTH + src_x]
                            if c != 0:
                                total += c
                                count += 1
                row.append(total // count if count > 0 else 0)
            scaled.append(row)

        # Rendu avec demi-blocs
        lines = []
        for row in range(0, len(scaled), 2):
            line_parts = []
            for col in range(len(scaled[0]) if scaled else 0):
                top_c = scaled[row][col]
                bot_c = scaled[row + 1][col] if row + 1 < len(scaled) else 0
                pal = HIRES_PALETTE
                r_top, g_top, b_top = pal[top_c] if top_c < len(pal) else (255, 255, 255)
                r_bot, g_bot, b_bot = pal[bot_c] if bot_c < len(pal) else (0, 0, 0)

                if top_c == bot_c:
                    line_parts.append(f"\033[38;2;{r_top};{g_top};{b_top}m█")
                else:
                    line_parts.append(
                        f"\033[38;2;{r_top};{g_top};{b_top};48;2;{r_bot};{g_bot};{b_bot}m▀"
                    )
            lines.append("".join(line_parts) + "\033[0m")
        return "\n".join(lines)
