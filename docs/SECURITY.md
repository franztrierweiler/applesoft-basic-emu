# AppleSoft BASIC Emulator — Sécurité

Version : 1.0
Date : 2026-03-15
Auteur : Franz TRIERWEILER / Claude (Anthropic)
Statut : Brouillon
Spec de référence : SPEC.md v1.0
Architecture de référence : ARCHITECTURE.md v1.0

## 1. Vue d'ensemble sécurité

L'émulateur Applesoft BASIC est un interpréteur de langage exécuté localement (CLI) ou dans un navigateur (page statique). Il ne traite aucune donnée sensible, ne communique avec aucun serveur, et n'expose aucune API réseau. Le profil de sécurité est minimal.

Les risques réels sont limités à trois vecteurs : l'exécution de programmes Applesoft potentiellement malveillants (sandboxing de l'émulateur), la supply chain des dépendances de développement, et les injections XSS dans le rendu web Phase 2.

**Classification des données :** Public
**Exposition réseau :** Aucune (CLI local + page statique)
**Référentiels appliqués :** OWASP (sélectif, Phase 2 uniquement), bonnes pratiques Python

## 2. Exigences de sécurité organisationnelles

| ID | Exigence | Description | Implémentation | Preuve de conformité | Statut |
|----|----------|-------------|----------------|----------------------|--------|
| SEC-ORG-01 | Pas de secrets dans le code | Aucun secret, token ou credential dans le code source | Pas de secret nécessaire (voir DEPLOYMENT.md § 2.4). Le seul token (GITHUB_TOKEN) est fourni automatiquement par GitHub Actions. | Scan du dépôt, absence de fichiers .env | ⏳ |
| SEC-ORG-02 | Revue de code | Toute modification significative est revue avant merge | Workflow SDD : `/sdd-dev-workflow` inclut revue des AC et tests | Historique PR / commits | ⏳ |
| SEC-ORG-03 | Tests avant commit | Ne jamais commiter de code sans tests unitaires réussis à 100% | Imposé par CLAUDE.md. Pipeline CI bloque le merge si les tests échouent. | Résultats CI, badge README | ⏳ |

## 3. Exigences de sécurité — Bonnes pratiques

### 3.1 Protection applicative

| ID | Exigence | Description | Implémentation | Preuve de conformité | Statut |
|----|----------|-------------|----------------|----------------------|--------|
| SEC-BP-01 | Sandboxing de l'émulateur | Un programme Applesoft ne doit pas pouvoir accéder au système hôte au-delà de ce que l'IOBridge autorise explicitement | L'Interpreter n'a accès qu'à l'Environment, au GraphicsEngine, au MemoryMap et à l'IOBridge. Aucun import `os`, `subprocess`, `eval`, `exec` dans le cœur. POKE et CALL sont limités à la dispatch table (voir ARCHITECTURE.md § 4.1, MemoryMap). | Revue de code : vérifier l'absence d'imports dangereux dans `src/` hors `io_bridge_cli.py` | ⏳ |
| SEC-BP-02 | Pas d'eval/exec sur du code utilisateur | Le code Applesoft est parsé et interprété via l'AST, jamais transmis à `eval()` ou `exec()` Python | Architecture Lexer → Parser → AST → Interpreter. Aucun chemin d'exécution ne passe par eval/exec. | Grep du code source pour `eval(` et `exec(` | ⏳ |
| SEC-BP-03 | Échappement HTML (Phase 2) | Les sorties PRINT ne doivent pas être interprétées comme du HTML dans le DOM | IOBridgeWeb utilise `textContent` (pas `innerHTML`) pour écrire dans la console DOM. Les caractères `<`, `>`, `&` sont échappés si insertion HTML nécessaire. | Tests d'intégration Phase 2 : programme Applesoft avec `PRINT "<script>alert(1)</script>"` ne provoque pas d'exécution JS | ⏳ |
| SEC-BP-04 | Limitation des boucles infinies | Un programme Applesoft avec boucle infinie ne doit pas geler le système | Phase 1 : Ctrl+C intercepté à chaque `step()` (flag vérifié). Phase 2 : time-slicing 50ms + bouton STOP. Voir ARCHITECTURE.md § 4.2 (flux step-by-step). | Tests : boucle `10 GOTO 10` interruptible en < 500ms | ⏳ |
| SEC-BP-05 | Limitation mémoire | Un programme Applesoft ne doit pas provoquer un épuisement mémoire de l'hôte | Taille des chaînes limitée à 255 caractères (EXG-028). Tableaux limités par DIM explicite. MemoryMap sparse limité à 64K adresses. Pas d'allocation dynamique non bornée. | Tests : programme tentant de créer des chaînes > 255 → erreur `?STRING TOO LONG` | ⏳ |

### 3.2 Supply chain

| ID | Exigence | Description | Implémentation | Preuve de conformité | Statut |
|----|----------|-------------|----------------|----------------------|--------|
| SEC-BP-10 | Zéro dépendance runtime | Aucune bibliothèque tierce en runtime. Seuls les modules Python stdlib autorisés. | Voir ARCHITECTURE.md § 3.1. Vérifiable par inspection de `pyproject.toml` (pas de `dependencies`). | `pip list` en environnement propre ne montre que la stdlib | ⏳ |
| SEC-BP-11 | Dépendances dev verrouillées | Les dépendances de développement (pytest, ruff, mypy) sont versionnées dans `pyproject.toml` | Versions minimales spécifiées dans `[project.optional-dependencies] dev = [...]` | Inspection de `pyproject.toml` | ⏳ |
| SEC-BP-12 | Audit des dépendances dev | Vérification périodique des vulnérabilités dans les dépendances de développement | `pip-audit` exécuté dans le pipeline CI (optionnel, à activer) | Rapport pip-audit dans les logs CI | ⏳ |

### 3.3 Intégrité du code

| ID | Exigence | Description | Implémentation | Preuve de conformité | Statut |
|----|----------|-------------|----------------|----------------------|--------|
| SEC-BP-20 | Analyse statique | Le code est vérifié par un linter et un type checker avant chaque merge | `make lint` (ruff + mypy) dans le pipeline CI. Voir DEPLOYMENT.md § 6. | Logs CI, zéro erreur ruff/mypy | ⏳ |
| SEC-BP-21 | Couverture de tests | La couverture de tests est mesurée et visible | pytest-cov dans le pipeline CI, badge dans le README | Rapport de couverture, badge | ⏳ |

## 4. Exigences de sécurité — Stack technique

### 4.1 Python

| ID | Exigence | Description | Implémentation | Preuve de conformité | Statut |
|----|----------|-------------|----------------|----------------------|--------|
| SEC-TECH-01 | Pas de pickle/marshal sur données non fiables | Aucune désérialisation de données binaires non fiables | Le projet ne fait aucune sérialisation binaire. SAVE/LOAD utilise du texte brut (format LIST). | Grep du code source pour `pickle`, `marshal`, `shelve` | ⏳ |
| SEC-TECH-02 | Pas d'accès filesystem dans le cœur | Seul IOBridgeCLI accède au filesystem (SAVE/LOAD). Le cœur est pur. | Voir ARCHITECTURE.md § 2, principe 1 (Python pur). | Grep de `open(`, `os.path`, `os.remove` dans `src/` hors `io_bridge_cli.py` et `png_writer.py` | ⏳ |
| SEC-TECH-03 | Validation des chemins fichiers (SAVE/LOAD) | Les noms de fichiers fournis par SAVE/LOAD ne doivent pas permettre de traverser l'arborescence | IOBridgeCLI valide le nom de fichier : pas de `/`, `..`, ou caractères spéciaux. Les fichiers sont écrits dans le répertoire courant uniquement. | Tests : `SAVE "../../../etc/passwd"` → erreur ou nom nettoyé | ⏳ |

### 4.2 Brython / Phase 2

| ID | Exigence | Description | Implémentation | Preuve de conformité | Statut |
|----|----------|-------------|----------------|----------------------|--------|
| SEC-TECH-10 | Pas d'innerHTML | L'IOBridgeWeb n'utilise jamais `innerHTML` pour injecter du texte utilisateur | Utilisation exclusive de `textContent` ou `createTextNode` | Grep du code `web/` pour `innerHTML` | ⏳ |
| SEC-TECH-11 | Événements clavier consommés | Les événements clavier capturés par la console appellent `preventDefault()` pour éviter les conflits navigateur | IOBridgeWeb appelle `event.preventDefault()` sur les événements routés vers l'émulateur (EXG-074) | Tests manuels : Ctrl+C ne copie pas, RETURN ne soumet pas de formulaire | ⏳ |
| SEC-TECH-12 | localStorage — pas de données sensibles | Le localStorage ne contient que des programmes Applesoft (texte brut) | Aucune donnée sensible à stocker. Les programmes sont du texte Applesoft pur. | Inspection du localStorage dans les DevTools navigateur | ⏳ |

## 5. Légende des statuts

| Statut | Signification |
|--------|---------------|
| ✅ | Implémenté et vérifié |
| 🔄 | En cours d'implémentation |
| ⏳ | Planifié (non démarré) |
| ❌ | Non applicable |
