# Revue de code — lot-06-graphisme

**Date :** 2026-04-09
**Fichiers revus :** 3 (graphics.py, interpreter.py §616-727, tests/qa/test_lot06_qa.py)

## Constats

| # | Fichier | Ligne | Axe | Sévérité | Constat | Recommandation |
|---|---------|-------|-----|----------|---------|----------------|
| R01 | src/applesoft/interpreter.py | — | Conformité | 🟠 | `interpreter.py` fait 1045 lignes, au-delà de la limite de 500 lignes par fichier (ARCHITECTURE.md ADR-006). Constat global au projet, pas spécifique au lot 06. | Planifier un refactoring de l'Interpreter pour extraire les sous-modules (graphisme, math, affichage, etc.) dans un lot futur. |
| R02 | src/applesoft/interpreter.py | 616-727 | Qualité | 🟡 | La section graphisme de l'Interpreter répète le même pattern `try: self.graphics.xxx() except ValueError: raise BasicError(53) from None` dans 10 méthodes. Duplication mineure mais lisible. | Envisager un décorateur ou une méthode utilitaire `_gfx_call()` pour factoriser le pattern. |
| R03 | src/applesoft/graphics.py | 275-372 | Qualité | 🟡 | La méthode `_render_shape` est longue (~100 lignes) avec imbrications profondes. Lisible mais pourrait bénéficier d'une extraction de la boucle de décodage des vecteurs. | Optionnel — pas de bug, complexité intrinsèque au format shape table Apple II. |
| R04 | src/applesoft/graphics.py | 405-455 | Performance | 🟡 | Le rendu HiRes downscale utilise une boucle quadruple imbriquée O(out_w * out_h * sx * sy). Pour les valeurs par défaut (sx=2, sy=2), cela donne ~107k itérations — acceptable pour du rendu ponctuel. | Acceptable — throttle 30 FPS protège en usage intensif. |

## Synthèse

- Conformité architecturale : ⚠️ — `graphics.py` (455 lignes) respecte la limite, mais `interpreter.py` (1045 lignes) la dépasse. Le composant GraphicsEngine est bien isolé conformément à ARCHITECTURE.md § 4.2.
- Sécurité : ✅ — Conforme aux 3 exigences SEC-DEV ciblées
  - SEC-DEV-01 : ✅ Pas de eval/exec/pickle/compile dans graphics.py
  - SEC-DEV-02 : ✅ Fail securely (ValueError dans GraphicsEngine → BasicError(53) dans Interpreter)
  - SEC-DEV-05 : ✅ Buffers bornés (bytearray 40x48=1920 et 280x192=53760), non extensibles
- Qualité du code : ✅ — Nommage cohérent, palettes documentées, code lisible. Duplication mineure dans l'Interpreter.
- Tests : ✅ — 35 tests unitaires + 44 tests QA couvrant les 44 scénarios du plan. Chaque CA-UC couvert. Nommage traçable (test_tXX_YY_description).
- Performance : ✅ — Bresenham O(max(dx,dy)), buffers bytearray efficaces. Rendu downscale acceptable.
