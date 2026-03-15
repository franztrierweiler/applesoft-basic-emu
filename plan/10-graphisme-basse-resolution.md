# EPIC 10 — Graphisme basse résolution

**Statut :** ⏳ Non démarré
**Priorité :** Critique
**Dépendances :** EPIC 05 (REPL + Commandes)
**Référence :** ARCHITECTURE.md § 4.1 (GraphicsEngine) — SPEC.md EXG-048 à EXG-054

## Objectif

Implémenter le mode graphique basse résolution : GR, COLOR=, PLOT, HLIN, VLIN, SCRN(). Implémenter le rendu CLI (ANSI/Unicode). À la fin de cet EPIC, un programme dessinant des formes colorées en basse résolution produit un rendu visible dans le terminal.

## Tâches

| # | Tâche | Statut |
|---|-------|--------|
| 10.1 | Implémenter `GraphicsEngine` : squelette, gestion des modes (TEXT, GR, HGR, HGR2), palette GR 16 couleurs | ⏳ |
| 10.2 | Implémenter le buffer GR (40×48, init noir) | ⏳ |
| 10.3 | Implémenter GR (activation mode, effacement buffer, zone texte 4 lignes) | ⏳ |
| 10.4 | Implémenter COLOR= (validation 0-15, troncature float) | ⏳ |
| 10.5 | Implémenter PLOT x,y (écriture buffer, validation coordonnées) | ⏳ |
| 10.6 | Implémenter HLIN x1,x2 AT y (ligne horizontale, inversion bornes si nécessaire) | ⏳ |
| 10.7 | Implémenter VLIN y1,y2 AT x (ligne verticale, inversion bornes si nécessaire) | ⏳ |
| 10.8 | Implémenter SCRN(x,y) (lecture buffer) | ⏳ |
| 10.9 | Implémenter le rendu CLI : caractères blocs Unicode (▀▄█) + couleurs ANSI 256 | ⏳ |
| 10.10 | Enrichir IOBridgeCLI avec `render_gr(buffer)` | ⏳ |
| 10.11 | Tests unitaires pour toutes les exigences couvertes (tests sur le buffer, pas sur le rendu visuel) | ⏳ |

## Exigences couvertes

| Exigence | Description | Statut tests |
|----------|-------------|-------------|
| EXG-048 | GR (activation mode basse résolution) | ⏳ |
| EXG-049 | COLOR= | ⏳ |
| EXG-050 | PLOT | ⏳ |
| EXG-051 | HLIN / VLIN | ⏳ |
| EXG-052 | SCRN() | ⏳ |
| EXG-053 | TEXT (retour mode texte) — partagé avec EPIC 07 | ⏳ |
| EXG-054 | Rendu CLI basse résolution | ⏳ |

## Critères d'acceptation (extraits SPEC.md)

| CA | Description | Statut |
|----|-------------|--------|
| CA-048-01 | GR active le mode, efface en noir, 4 lignes texte | ⏳ |
| CA-048-02 | GR + PRINT → texte dans la zone texte | ⏳ |
| CA-049-01 | `COLOR=1 : PLOT 5,5` → magenta en (5,5) | ⏳ |
| CA-050-01 | PLOT place un bloc dans le buffer | ⏳ |
| CA-051-01 | HLIN trace une ligne horizontale | ⏳ |
| CA-051-02 | VLIN trace une ligne verticale | ⏳ |
| CA-051-03 | HLIN avec bornes inversées → trace quand même | ⏳ |
| CA-052-01 | SCRN(5,5) après PLOT → retourne la couleur | ⏳ |
| CA-052-02 | SCRN(0,0) après GR → 0 (noir) | ⏳ |
| CA-054-01 | Rendu visible dans le terminal | ⏳ |

## Cas limites à tester

| CL | Description | Statut |
|----|-------------|--------|
| CL-048-01 | GR deux fois → effacement à chaque appel | ⏳ |
| CL-049-01 | `COLOR= -1` → `?ILLEGAL QUANTITY ERROR` | ⏳ |
| CL-049-02 | `COLOR= 16` → `?ILLEGAL QUANTITY ERROR` | ⏳ |
| CL-049-03 | `COLOR= 5.9` → tronqué à 5 | ⏳ |
| CL-050-01 | `PLOT 40,0` → `?ILLEGAL QUANTITY ERROR` | ⏳ |
| CL-050-02 | `PLOT 0,48` → `?ILLEGAL QUANTITY ERROR` | ⏳ |
| CL-052-01 | `SCRN(40,0)` → `?ILLEGAL QUANTITY ERROR` | ⏳ |

## Livrables

- `src/graphics_engine.py` — moteur graphique (GR)
- `src/io_bridge_cli.py` — enrichi (rendu ANSI GR)
- `tests/unit/test_graphics_engine.py`
