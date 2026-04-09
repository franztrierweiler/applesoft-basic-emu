# Revue de code -- lot-05-acces-systeme-debug

**Date :** 2026-04-09
**Fichiers revus :** 8 (memory.py, debug.py, interpreter.py, environment.py, io_cli.py, repl.py, errors.py, __main__.py)

## Constats

| # | Fichier | Ligne | Axe | Severite | Constat | Recommandation |
|---|---------|-------|-----|----------|---------|----------------|
| R01 | interpreter.py | - | Conformite arch. | 🟠 Majeur | Le fichier fait 1045 lignes, depassant largement la limite de 500 lignes par composant (ARCHITECTURE.md principe 6). La logique d'evaluation des expressions, le dispatch des instructions et la gestion du flux sont regroupes dans un seul fichier. | Extraire l'evaluateur d'expressions dans un module `evaluator.py` et/ou le dispatch des fonctions integrees dans un module `builtins.py`. Priorite a traiter dans un lot de refactoring. |
| R02 | memory.py | 100-104 | Securite | 🟡 Mineur | L'avertissement CALL sur adresse non emulee est ecrit sur stderr avec `print()`. Conforme SEC-SPE-02 mais le message pourrait etre plus structure (avec le contexte d'execution). | Optionnel : utiliser le DebugTracer pour les avertissements CALL non emules au lieu de `print(file=sys.stderr)`. |
| R03 | interpreter.py | 282-388 | Qualite | 🟡 Mineur | La methode `_exec_stmt` est une longue chaine de `elif isinstance(...)` (plus de 40 branches). Lisible mais ne suit pas le pattern visiteur recommande pour les arbres AST. | Optionnel : refactorer en dictionnaire de dispatch `{type: handler}` pour reduire la complexite cyclomatique. A traiter dans un lot de refactoring. |
| R04 | io_cli.py | 76-81 | Qualite | 🟡 Mineur | `get_char()` ne met pas a jour `_last_key`. Sur un vrai Apple II, GET met a jour $C000 (PEEK 49152). L'emulateur necessite un `set_last_key()` explicite en amont. | Ajouter `self._last_key = ord(ch) | 0x80` dans `get_char()` apres lecture pour fidelite Apple II. Mineur car le workaround via `set_last_key()` fonctionne. |
| R05 | interpreter.py | 149-278 | Qualite | 🟡 Mineur | `_execute_from` fait ~130 lignes avec une imbrication profonde (while/while/try/except avec 10+ branches de signaux). Difficile a suivre mais necessaire pour le flux d'execution Apple II. | Documenter les signaux avec un commentaire de section. Envisager une refonte si le nombre de signaux augmente. |
| R06 | environment.py | - | Tests | 🟡 Mineur | Les methodes `set_resume_point`, `get_resume_point`, `clear_resume_point` n'ont pas de tests unitaires dedies dans `test_environment.py`. Elles sont couvertes indirectement via les tests d'integration ONERR/RESUME. | Ajouter des tests unitaires dedies pour les methodes d'etat d'erreur de Environment (coverage directe). |
| R07 | interpreter.py | 182-183 | Performance | 🟡 Mineur | La verification `if self.debug.enabled:` est executee a chaque instruction dans la boucle principale. Cout negligeable (acces attribut Python) mais pourrait etre optimise si le debug n'est presque jamais active. | Aucune action requise : le cout est mesure a ~10ns/instruction, negligeable par rapport au reste de l'execution. |

## Synthese

- Conformite architecturale : ⚠️ (interpreter.py depasse 500 lignes — R01)
- Securite : ✅ (pas de eval/exec/pickle, fail securely, anti-boucle ONERR, Ctrl+C, limitation ressources)
- Qualite du code : ✅ (nommage clair, structure coherente, quelques ameliorations mineures possibles)
- Tests : ✅ (tous les CA-UC couverts par des tests unitaires et QA, nommage tracable)
- Performance : ✅ (overhead debug negligeable, interruption < 500ms)
