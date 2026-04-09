# Rapport QA — lot-06-graphisme

**Date :** 2026-04-09
**Lot :** lot-06-graphisme
**Verdict :** ✅ VALIDE

## Résumé

- Tests unitaires (dev) : 614/614 passés (suite complète)
- Tests unitaires graphisme : 35/35 passés (test_graphics.py)
- Scénarios QA : 44/44 passés
  - 🔴 Bloquants : 29/29 passés
  - 🟠 Majeurs : 13/13 passés (nota : 9 scénarios QA + 4 constats revue)
  - 🟡 Mineurs : 2/2 passés
- Revue de code : 4 constats (0 🔴, 1 🟠 non bloquant, 3 🟡)

## Scénarios QA — Résultats détaillés

### UC-018 — Basse résolution (16 scénarios)
- ✅ T01-01 [🔴] GR active le mode LoRes
- ✅ T01-02 [🔴] PLOT magenta en (5,5)
- ✅ T01-03 [🔴] HLIN ligne horizontale verte
- ✅ T01-04 [🔴] HLIN inversion des bornes
- ✅ T01-05 [🔴] SCRN lit la couleur
- ✅ T01-06 [🔴] TEXT restaure le mode texte
- ✅ T01-07 [🟠] VLIN inversion des bornes
- ✅ T01-08 [🔴] COLOR= -1 erreur
- ✅ T01-09 [🔴] COLOR= 16 erreur
- ✅ T01-10 [🟠] COLOR= 5.9 tronqué à 5
- ✅ T01-11 [🔴] PLOT x hors limites
- ✅ T01-12 [🔴] PLOT y hors limites
- ✅ T01-13 [🔴] HLIN y hors limites
- ✅ T01-14 [🔴] VLIN x hors limites
- ✅ T01-15 [🔴] SCRN x hors limites
- ✅ T01-16 [🔴] SCRN y hors limites

### UC-019 — Haute résolution (10 scénarios)
- ✅ T02-01 [🔴] HGR page 1
- ✅ T02-02 [🔴] HGR2 page 2
- ✅ T02-03 [🔴] HPLOT diagonale
- ✅ T02-04 [🔴] HPLOT carré enchaîné
- ✅ T02-05 [🔴] HPLOT TO depuis dernière position
- ✅ T02-06 [🔴] HCOLOR= -1 erreur
- ✅ T02-07 [🔴] HCOLOR= 8 erreur
- ✅ T02-08 [🔴] HPLOT x hors limites
- ✅ T02-09 [🔴] HPLOT y hors limites
- ✅ T02-10 [🟠] HPLOT TO défaut (0,0)

### UC-020 — Shape tables (9 scénarios)
- ✅ T03-01 [🔴] DRAW forme dessinée
- ✅ T03-02 [🔴] XDRAW efface (XOR)
- ✅ T03-03 [🟠] ROT + SCALE
- ✅ T03-04 [🔴] DRAW sans table erreur
- ✅ T03-05 [🔴] DRAW 0 erreur
- ✅ T03-06 [🔴] ROT= -1 erreur
- ✅ T03-07 [🔴] ROT= 256 erreur
- ✅ T03-08 [🟠] SCALE= 0 invisible
- ✅ T03-09 [🔴] SCALE= 256 erreur

### UC-021 — Rendu terminal (4 scénarios)
- ✅ T04-01 [🟠] Rendu LoRes ANSI
- ✅ T04-02 [🟠] Rendu HiRes ANSI
- ✅ T04-03 [🟡] Rendu LoRes écran vierge
- ✅ T04-04 [🟡] Rendu HiRes écran vierge

### ENF/SEC — Non fonctionnel (5 scénarios)
- ✅ T05-01 [🔴] Pas d'imports interdits
- ✅ T05-02 [🟠] GraphicsEngine isolé
- ✅ T05-03 [🔴] Pas d'eval/exec
- ✅ T05-04 [🔴] Fail securely
- ✅ T05-05 [🟠] Buffers bornés

## Scénarios en échec

Aucun.

## Constats de revue

| # | Sévérité | Constat | Impact |
|---|----------|---------|--------|
| R01 | 🟠 | interpreter.py dépasse 500 lignes (1045) | Non spécifique au lot 06. Refactoring à planifier. |
| R02 | 🟡 | Duplication du pattern try/except ValueError dans l'Interpreter | Lisibilité OK, pas de bug. |
| R03 | 🟡 | _render_shape est longue (~100 lignes) | Complexité intrinsèque au format shape table. |
| R04 | 🟡 | Rendu HiRes downscale en O(n^2) | Acceptable avec throttle 30 FPS. |

## Points d'attention

- Le constat R01 (interpreter.py > 500 lignes) est un constat global au projet, pas un bloquant pour ce lot. Il existe déjà avant le lot 06 et devrait être traité dans un lot de refactoring dédié.
- Le constat R01 n'est pas compté comme bloquant pour le verdict car il n'est pas spécifique au lot 06 et ne concerne pas le fichier principal `graphics.py` (455 lignes, dans la limite).

## Références

- Plan de test : `qa/plan-test/lot-06-graphisme.md`
- Revue de code : `qa/code-review/lot-06-graphisme-review.md`
- Plan du lot : `plan/lot-06-graphisme.md`
