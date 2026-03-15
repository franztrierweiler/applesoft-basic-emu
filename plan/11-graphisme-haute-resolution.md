# EPIC 11 — Graphisme haute résolution

**Statut :** ⏳ Non démarré
**Priorité :** Critique
**Dépendances :** EPIC 10 (Graphisme basse résolution)
**Référence :** ARCHITECTURE.md § 4.1 (GraphicsEngine, LineRenderer, PNGWriter) — SPEC.md EXG-055 à EXG-060

## Objectif

Implémenter le mode graphique haute résolution : HGR/HGR2, HCOLOR=, HPLOT (point et ligne avec Bresenham). Implémenter l'export PNG en Python pur. Les shape tables (DRAW/XDRAW, EXG-058/059) sont différées — l'interface est prévue mais l'implémentation est reportée.

## Tâches

| # | Tâche | Statut |
|---|-------|--------|
| 11.1 | Implémenter le buffer HGR (280×192, init noir) dans GraphicsEngine | ⏳ |
| 11.2 | Implémenter HGR (page 1, mode mixte 280×160 + 4 lignes texte) | ⏳ |
| 11.3 | Implémenter HGR2 (page 2, plein écran 280×192) | ⏳ |
| 11.4 | Implémenter HCOLOR= (validation 0-7, palette HGR) | ⏳ |
| 11.5 | Implémenter HPLOT x,y (point unique) | ⏳ |
| 11.6 | Implémenter `LineRenderer` (algorithme de Bresenham) | ⏳ |
| 11.7 | Implémenter HPLOT x1,y1 TO x2,y2 (ligne) et enchaînement TO | ⏳ |
| 11.8 | Implémenter HPLOT TO x,y (depuis dernière position) | ⏳ |
| 11.9 | Implémenter `PNGWriter` (écriture PNG minimal en Python pur) | ⏳ |
| 11.10 | Implémenter le rendu CLI HGR : demi-blocs Unicode + couleurs ANSI, et export PNG | ⏳ |
| 11.11 | Enrichir IOBridgeCLI avec `render_hgr(buffer)` et export PNG | ⏳ |
| 11.12 | Stub pour DRAW/XDRAW/ROT=/SCALE= (erreur ou no-op documenté) | ⏳ |
| 11.13 | Tests unitaires pour toutes les exigences couvertes | ⏳ |

## Exigences couvertes

| Exigence | Description | Statut tests |
|----------|-------------|-------------|
| EXG-055 | HGR / HGR2 | ⏳ |
| EXG-056 | HCOLOR= | ⏳ |
| EXG-057 | HPLOT (point, ligne, enchaînement) | ⏳ |
| EXG-058 | DRAW / XDRAW (stub, différé) | ⏳ |
| EXG-059 | ROT= / SCALE= (stub, différé) | ⏳ |
| EXG-060 | Rendu CLI haute résolution | ⏳ |

## Critères d'acceptation (extraits SPEC.md)

| CA | Description | Statut |
|----|-------------|--------|
| CA-055-01 | HGR active page 1, écran noir, 4 lignes texte | ⏳ |
| CA-055-02 | HGR2 active page 2, plein écran | ⏳ |
| CA-056-01 | `HCOLOR=1 : HPLOT 0,0 TO 100,0` → ligne verte | ⏳ |
| CA-056-02 | `HCOLOR=3 : HPLOT 140,80` → point blanc au centre | ⏳ |
| CA-057-01 | HPLOT point unique | ⏳ |
| CA-057-02 | HPLOT ligne diagonale | ⏳ |
| CA-057-03 | HPLOT enchaînement TO (carré) | ⏳ |
| CA-057-04 | HPLOT TO depuis dernière position | ⏳ |
| CA-060-01 | Rendu visible en terminal ou export PNG | ⏳ |

## Cas limites à tester

| CL | Description | Statut |
|----|-------------|--------|
| CL-055-01 | HGR deux fois → effacement | ⏳ |
| CL-055-02 | HGR2 + PRINT → texte non visible | ⏳ |
| CL-056-01 | `HCOLOR= -1` → `?ILLEGAL QUANTITY ERROR` | ⏳ |
| CL-056-02 | `HCOLOR= 8` → `?ILLEGAL QUANTITY ERROR` | ⏳ |
| CL-057-01 | `HPLOT 280,0` → `?ILLEGAL QUANTITY ERROR` | ⏳ |
| CL-057-02 | `HPLOT 0,192` → `?ILLEGAL QUANTITY ERROR` | ⏳ |
| CL-057-03 | `HPLOT TO 50,50` sans HPLOT préalable → position par défaut (0,0) | ⏳ |

## Livrables

- `src/graphics_engine.py` — enrichi (HGR)
- `src/line_renderer.py` — Bresenham
- `src/png_writer.py` — export PNG Python pur
- `src/io_bridge_cli.py` — enrichi (rendu HGR + export)
- `tests/unit/test_line_renderer.py`
- `tests/unit/test_png_writer.py`
- `tests/unit/test_graphics_engine.py` — enrichi
