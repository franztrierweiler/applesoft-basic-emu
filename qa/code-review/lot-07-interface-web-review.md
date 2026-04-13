# Revue de code — lot-07-interface-web

**Date :** 2026-04-10
**Fichiers revus :** 3 (web/io_web.py, web/index.html, web/style.css)

## Constats

| # | Fichier | Ligne | Axe | Sévérité | Constat | Recommandation |
|---|---------|-------|-----|----------|---------|----------------|
| R01 | web/io_web.py | 1-837 | Qualité | 🟠 Majeur | io_web.py fait 837 lignes — dépasse le seuil de 500 lignes recommandé | Envisager un découpage en modules (highlight.py, persistence.py, canvas.py) dans une itération future. Non bloquant car le fichier est bien structuré avec des sections clairement délimitées. |
| R02 | web/io_web.py | 257-263 | Performance | 🟡 Mineur | `_match_keyword` itère sur toute la liste de mots-clés à chaque position — complexité O(n*k) par ligne | Pré-construire un trie ou trier par longueur décroissante pour sortir plus tôt. Impact marginal sur des lignes BASIC courtes. |
| R03 | web/io_web.py | 325 | Qualité | 🟡 Mineur | `import json` à l'intérieur de chaque méthode de persistance | Déplacer l'import en tête de fichier (après les imports Brython). Mineur car Brython cache les modules importés. |
| R04 | web/io_web.py | 46-61 | Qualité | 🟡 Mineur | `__init__` initialise 13 attributs — acceptable mais à surveiller | Regrouper les attributs liés à l'input async dans un dataclass/namedtuple si le nombre augmente. |
| R05 | web/io_web.py | 739-794 | Qualité | 🟡 Mineur | `_bind_toolbar` fait 60 lignes avec closures imbriquées | Extraire chaque handler en méthode nommée pour lisibilité. Non bloquant. |

## Synthèse

- Conformité architecturale : ✅ — IOBridgeWeb est le seul module important `browser`. Structure `web/` conforme à ARCHITECTURE.md § 7. Séparation cœur/IO respectée.
- Sécurité : ✅ — 0 innerHTML, 7 textContent, validation fichiers (SEC-BP-40/41), pas de CDN (SEC-SDLC-03), pas d'eval/exec/pickle (SEC-DEV-01). XSS prévenu par textContent exclusif.
- Qualité du code : ⚠️ — io_web.py dépasse 500 lignes (🟠). Code bien structuré et documenté malgré la taille. Nommage cohérent, commentaires traçables aux UC/CA.
- Tests : ✅ — 81 tests unitaires + 40 scénarios QA. Chaque CA-UC couvert. Nommage traçable (test_t07_xx_...). Tests structurels + fonctionnels (time-slicing pur Python).
- Performance : ✅ — Time-slicing fonctionnel (yield ~50ms). Rendu canvas via fillRect. Highlighting par ligne (pas de reflow complet du DOM).
