# AppleSoft BASIC Emulator — Sécurité

Version : 1.0
Date : 2026-04-06
Auteur : Franz / Claude
Statut : Validé
Spec de référence : SPEC-racine-ApplesoftBasicEmu.md v3.1
Architecture de référence : ARCHITECTURE.md v1.0

## 1. Vue d'ensemble sécurité

L'émulateur Applesoft BASIC est une application locale (CLI + fichier HTML ouvert dans un navigateur) sans composant réseau, sans authentification et sans données sensibles. La surface d'attaque est réduite : les seuls points d'entrée sont la saisie utilisateur via le REPL et le chargement de fichiers `.bas`. Les risques principaux sont l'injection de code Python via l'interpréteur BASIC, le path traversal via SAVE/LOAD, et la supply chain des dépendances. Le profil de sécurité est léger mais les bonnes pratiques de développement sécurisé s'appliquent.

**Classification des données :** Public (aucune donnée sensible)
**Exposition réseau :** Isolé (application locale, pas de serveur, pas de communication réseau)
**Référentiels appliqués :** OWASP Secure Coding Practices (principes de développement sécurisé)
**Référentiels sectoriels :** Aucun (SPEC-racine-ApplesoftBasicEmu.md § Contraintes structurantes : « Aucune contrainte réglementaire ou normative »)

## 2. Modèle de menaces

### 2.1 Surface d'attaque

| Point d'entrée | Type | Exposition | Données accessibles | Niveau de risque |
|----------------|------|-----------|---------------------|-----------------|
| Saisie REPL (CLI) | stdin | Local uniquement | Programme en mémoire, variables | Faible |
| Fichier .bas (LOAD CLI) | Fichier local | Local uniquement | Programme en mémoire, système de fichiers (via SAVE) | Modéré |
| Fichier .bas (import/drag & drop Phase 2) | Fichier utilisateur | Local navigateur | Programme en mémoire, localStorage, DOM | Modéré |
| Commande SAVE | Écriture fichier | Local uniquement | Système de fichiers dans le répertoire projet | Modéré |
| Brython (Phase 2) | Bibliothèque JS embarquée | Locale (incluse dans le projet) | Contexte de la page web | Faible (inclus en local) |
| Pillow (CLI) | Dépendance Python | Installation locale | Système de fichiers (export PNG) | Faible |

### 2.2 Acteurs malveillants

| Acteur | Motivation | Capacités | Cibles principales |
|--------|-----------|-----------|-------------------|
| Fichier .bas piégé | Exploiter un bug du parser ou de l'interpréteur pour exécuter du code Python arbitraire | Fourni par un tiers (téléchargé, partagé), chargé volontairement par l'utilisateur | Interpréteur (injection), SAVE (path traversal) |
| Supply chain compromise | Compromettre une dépendance pour exécuter du code malveillant | Mainteneur malveillant ou compte compromis sur PyPI | Pillow (CLI), Brython (Phase 2) |

### 2.3 Frontières de confiance

| Frontière | De | Vers | Contrôles requis |
|-----------|-----|------|-----------------|
| Saisie utilisateur → REPL | Entrée non fiable | Moteur d'exécution | Tokenisation stricte (Lexer), parsing structuré (Parser), jamais `eval`/`exec` |
| Fichier .bas → LOAD | Fichier externe non fiable | Programme en mémoire | Même pipeline Lexer→Parser, validation du format, rejet des lignes invalides |
| SAVE → Système de fichiers | Moteur d'exécution | Système de fichiers local | Restriction au répertoire projet, validation du nom de fichier |
| Contenu BASIC → DOM (Phase 2) | Données internes | Affichage HTML | Échappement du contenu avant insertion dans le DOM |

## 3. Exigences de sécurité organisationnelles

| ID | Exigence | Description | Implémentation | Preuve de conformité | Statut |
|----|----------|-------------|----------------|----------------------|--------|
| SEC-ORG-01 | Pas de secrets dans le code | Aucun secret, clé ou credential dans le dépôt (même si le projet n'en utilise pas, la règle est de principe) | Vérification manuelle, `.gitignore` couvre `.env` | Revue avant chaque release | ⏳ |
| SEC-ORG-02 | Développement sur branche main | Le pilote développe avec Claude Code sur `main`. Branches expérimentales sur instruction explicite (voir CLAUDE.md). | Convention documentée dans CLAUDE.md | Historique git | ✅ |
| SEC-ORG-03 | Tests avant release | Aucun code n'est releasé sans `make test` + `make lint` à 100% | Procédure de release documentée dans DEPLOYMENT.md § 7 | Exit codes des commandes | ⏳ |

## 4. Exigences de sécurité — Bonnes pratiques

Les sections 4.1 (Authentification), 4.2 (Sessions), 4.3 (Cryptographie), 4.6 (API), 4.9 (Segmentation réseau) et 4.10 (Continuité) ne s'appliquent pas à ce projet (application locale, pas de réseau, pas d'authentification, pas de données chiffrées). Elles sont omises.

### 4.4 Protection applicative

| ID | Exigence | Description | Implémentation | Preuve de conformité | Statut |
|----|----------|-------------|----------------|----------------------|--------|
| SEC-BP-20 | Pas d'injection Python | L'interpréteur BASIC ne doit jamais utiliser `eval()`, `exec()`, `compile()` ou `__import__()` pour évaluer du code BASIC | Le Parser produit un AST typé, l'Interpreter parcourt l'AST avec un visiteur dédié. Aucune évaluation dynamique de code Python. | Règle ruff interdisant `eval`/`exec` dans `src/`, revue de code, grep automatisé | ⏳ |
| SEC-BP-21 | Validation des entrées numériques | Les valeurs passées à PEEK, POKE, CALL, COLOR=, HCOLOR= sont validées dans les plages autorisées avant traitement | Vérification systématique des bornes dans l'Interpreter, `?ILLEGAL QUANTITY ERROR` si hors plage (RG-0010) | Tests unitaires sur les bornes, CA du SPEC-racine-ApplesoftBasicEmu.md | ⏳ |
| SEC-BP-22 | Path traversal — restriction SAVE/LOAD | SAVE et LOAD sont restreints au répertoire du projet Python. Les chemins absolus, `..`, et les liens symboliques sont refusés. | Résolution du chemin canonique (`os.path.realpath`), vérification que le chemin résolu est sous le répertoire projet, rejet sinon | Tests unitaires avec chemins malveillants (`../../etc/passwd`, `/tmp/evil`, liens symboliques) | ⏳ |
| SEC-BP-23 | Validation du contenu des fichiers .bas | LOAD ne charge que des fichiers texte contenant des lignes BASIC valides. Les lignes non parsables sont rejetées avec un message d'erreur. | Chaque ligne chargée passe par le Lexer. Les erreurs de tokenisation sont signalées sans arrêter le chargement. | Tests avec fichiers .bas malformés, binaires, encodages invalides | ⏳ |
| SEC-BP-24 | XSS — échappement DOM (Phase 2) | Tout contenu BASIC affiché dans le DOM (PRINT, LIST, messages d'erreur) est échappé avant insertion | Utilisation de `textContent` (pas `innerHTML`) dans l'IOBridgeWeb pour tout texte provenant de l'interpréteur | Revue de code, tests avec caractères `<script>`, `<img onerror=...>` dans les chaînes BASIC | ⏳ |
| SEC-BP-25 | Taille maximale des fichiers .bas | LOAD refuse les fichiers dépassant une taille raisonnable pour prévenir les dénis de service mémoire | Limite à 1 Mo (largement suffisant pour tout programme Applesoft, un programme réel dépasse rarement 50 Ko) | Test avec fichier surdimensionné | ⏳ |

### 4.5 Gestion des erreurs et fuites d'information

| ID | Exigence | Description | Implémentation | Preuve de conformité | Statut |
|----|----------|-------------|----------------|----------------------|--------|
| SEC-BP-30 | Messages d'erreur Applesoft uniquement | Les erreurs d'exécution BASIC produisent les messages Applesoft standardisés (RG-0010). Aucune stack trace Python n'est exposée à l'utilisateur. | L'Interpreter capture les exceptions Python internes et les traduit en erreurs Applesoft. Les exceptions non prévues sont capturées par un handler global qui affiche un message générique. | Tests d'erreur, vérification de l'absence de tracebacks dans la sortie | ⏳ |
| SEC-BP-31 | Pas d'information système exposée | L'émulateur ne révèle pas de chemins filesystem, versions Python, ou informations système dans ses messages | Revue des messages d'erreur, pas de `str(exception)` exposé directement | Revue de code | ⏳ |

### 4.7 Upload et stockage de fichiers

| ID | Exigence | Description | Implémentation | Preuve de conformité | Statut |
|----|----------|-------------|----------------|----------------------|--------|
| SEC-BP-40 | Validation des fichiers importés (Phase 2) | Le drag & drop et le bouton LOAD n'acceptent que des fichiers texte (.bas, .txt). Les fichiers binaires sont rejetés. | Vérification de l'extension et du contenu (doit être décodable en UTF-8 ou ASCII) | Tests avec fichiers binaires, images, exécutables | ⏳ |
| SEC-BP-41 | Limite de taille import (Phase 2) | Les fichiers importés via le navigateur sont limités à 1 Mo | Vérification `File.size` avant lecture | Test avec fichier surdimensionné | ⏳ |

### 4.8 Journalisation et détection

| ID | Exigence | Description | Implémentation | Preuve de conformité | Statut |
|----|----------|-------------|----------------|----------------------|--------|
| SEC-BP-50 | Mode debug ne log pas de données sensibles | Le DebugTracer n'affiche que l'état d'exécution BASIC (lignes, instructions, variables BASIC). Il ne log jamais de chemins filesystem, d'état Python interne, ou de données système. | Revue du format de sortie du DebugTracer | Tests du mode debug, revue de code | ⏳ |

## 5. Exigences de sécurité — Référentiels sectoriels

Non applicable. Le SPEC-racine-ApplesoftBasicEmu.md indique explicitement « Aucune contrainte réglementaire ou normative ».

## 6. Principes de développement sécurisé

| ID | Principe | Description | Exemples d'implémentation | Vérification |
|----|----------|-------------|--------------------------|-------------|
| SEC-DEV-01 | Pas de désérialisation non fiable | Ne jamais utiliser `eval()`, `exec()`, `pickle.loads()`, `compile()` sur des données provenant de l'utilisateur ou d'un fichier .bas | L'interpréteur BASIC utilise un AST typé produit par un parser structuré. Le Lexer et le Parser ne délèguent jamais à l'évaluateur Python. | Règle ruff/grep : `eval\(`, `exec\(`, `pickle`, `compile\(` = 0 occurrence dans `src/` |
| SEC-DEV-02 | Fail securely | En cas d'erreur non prévue dans l'interpréteur, le système affiche un message générique et revient au prompt REPL. Il ne crash pas, ne révèle pas d'information interne, et ne laisse pas l'environnement dans un état incohérent. | Handler global `try/except` dans la boucle REPL. Reset de l'état d'exécution si nécessaire. | Tests avec entrées malformées, fuzzing du Lexer/Parser |
| SEC-DEV-03 | Encodage des sorties contextualisé (Phase 2) | Toute donnée BASIC insérée dans le DOM est traitée comme du texte brut, jamais comme du HTML | `element.textContent = value` (pas `element.innerHTML = value`) dans IOBridgeWeb | Grep : `innerHTML` = 0 occurrence dans `web/io_web.py` (sauf si justifié et échappé) |
| SEC-DEV-04 | Validation des chemins fichier | Tout chemin de fichier fourni par l'utilisateur (SAVE, LOAD) est canonicalisé et vérifié avant utilisation | `os.path.realpath()` + vérification que le résultat est sous le répertoire projet | Tests unitaires avec chemins adverses |
| SEC-DEV-05 | Limitation des ressources | L'interpréteur protège contre les dénis de service : boucles infinies (Ctrl+C, UC-024), chaînes > 255 chars (RG-0007), piles GOSUB/FOR bornées, fichiers .bas < 1 Mo | Vérifications dans l'Interpreter et l'IOBridge | Tests avec programmes adverses (boucles, récursion profonde, chaînes géantes) |

## 7. SDLC sécurisé et supply chain

| ID | Exigence | Description | Implémentation | Preuve de conformité | Statut |
|----|----------|-------------|----------------|----------------------|--------|
| SEC-SDLC-01 | Lint de sécurité | Ruff est configuré pour détecter les patterns dangereux (eval, exec, assert utilisé pour la validation, etc.) | Règles ruff activées : `S` (bandit/security), `S102` (exec), `S307` (eval) | `make lint` sans erreur S* | ⏳ |
| SEC-SDLC-02 | Audit des dépendances | Vérification des vulnérabilités connues dans Pillow avant chaque release | `pip audit` exécuté manuellement avant release | Rapport pip-audit | ⏳ |
| SEC-SDLC-03 | Brython embarqué (pas de CDN) | Brython est inclus en local dans `web/` pour éliminer le risque de supply chain réseau. La version est figée et vérifiée. | Fichier Brython copié dans le dépôt, hash SHA-256 documenté | Hash du fichier vérifié, pas de chargement CDN dans `index.html` | ⏳ |
| SEC-SDLC-04 | Dépendances minimales | Le cœur de l'interpréteur n'a aucune dépendance externe (ENF-001). Pillow est la seule dépendance runtime, optionnelle. | Vérification dans CI : `import` dans `src/applesoft/` ne référence que la stdlib Python | Script de vérification des imports | ⏳ |
| SEC-SDLC-05 | Revue avant release | Le pilote vérifie les changements avant chaque tag et release GitHub | Procédure de release (DEPLOYMENT.md § 7) incluant `make lint` + `make test` | Historique git, tags annotés | ⏳ |

## 8. Exigences de sécurité — Stack technique

### 8.1 Python

| ID | Exigence | Description | Implémentation | Preuve de conformité | Statut |
|----|----------|-------------|----------------|----------------------|--------|
| SEC-TECH-01 | Pas d'eval/exec | Aucune utilisation de `eval()`, `exec()`, `compile()`, `__import__()` dans le code de l'émulateur | AST typé + visiteur pour l'évaluation des expressions BASIC | Règle ruff S307/S102, grep automatisé | ⏳ |
| SEC-TECH-02 | Gestion sûre des fichiers | Utilisation de `with open(...)` systématique, pas de fichiers laissés ouverts en cas d'erreur | Context managers Python | Revue de code | ⏳ |
| SEC-TECH-03 | Pas d'accès filesystem dans le cœur | Le cœur de l'interpréteur (Lexer, Parser, Interpreter, Environment, GraphicsEngine, MemoryMap) n'accède jamais au filesystem directement. Seul l'IOBridge gère les fichiers. | Architecture en oignon (ARCHITECTURE.md § 2, principe 2) | Grep : `open(`, `os.path`, `pathlib` = 0 dans les modules cœur | ⏳ |

### 8.2 Brython (Phase 2)

| ID | Exigence | Description | Implémentation | Preuve de conformité | Statut |
|----|----------|-------------|----------------|----------------------|--------|
| SEC-TECH-10 | Brython embarqué et versionné | Brython est inclus dans le dépôt, pas chargé depuis un CDN. La version est figée et documentée. | Fichiers `brython.js` et `brython_stdlib.js` dans `web/`, hash SHA-256 dans ce document ou dans un fichier `web/CHECKSUMS.sha256` | Vérification du hash, pas de `<script src="https://...">` dans `index.html` | ⏳ |
| SEC-TECH-11 | Isolation DOM | L'IOBridgeWeb est la seule couche accédant au DOM (RG-0014). Le cœur Python ne manipule jamais d'objets `browser`. | Architecture en oignon, `import browser` uniquement dans `io_web.py` | Grep : `import browser` = 0 dans `src/applesoft/` | ⏳ |
| SEC-TECH-12 | Pas d'innerHTML non échappé | Aucune insertion de contenu utilisateur via `innerHTML` ou équivalent Brython | `textContent` pour tout texte, `canvas` API pour les graphiques | Grep dans `web/io_web.py` | ⏳ |

### 8.3 Pillow (CLI, optionnel)

| ID | Exigence | Description | Implémentation | Preuve de conformité | Statut |
|----|----------|-------------|----------------|----------------------|--------|
| SEC-TECH-20 | Import conditionnel | Pillow n'est importé que si l'export PNG est demandé. Son absence ne bloque pas l'émulateur. | `try: from PIL import Image except ImportError: ...` dans `io_cli.py` | Test sans Pillow installé | ⏳ |
| SEC-TECH-21 | Écriture PNG restreinte | L'export PNG écrit dans le répertoire projet uniquement (même restriction que SAVE). | Même validation de chemin que SEC-BP-22 | Tests avec chemins adverses | ⏳ |

## 9. Réponse à incident

### 9.1 Rôles et responsabilités

| Rôle | Responsable | Responsabilités |
|------|------------|-----------------|
| Responsable incident | Franz (pilote du projet) | Investigation, correction, communication |

Le projet étant un outil open source local sans utilisateurs enregistrés ni données collectées, la réponse à incident se limite à la correction de la vulnérabilité et à la publication d'une release corrective.

### 9.2 Procédure de réponse

| Phase | Actions | Délai cible |
|-------|---------|-------------|
| **1. Détection** | Signalement via GitHub Issues ou découverte lors du développement | — |
| **2. Évaluation** | Évaluer la sévérité : le bug peut-il être exploité pour exécuter du code arbitraire, écrire des fichiers hors périmètre, ou crasher l'émulateur ? | < 24h |
| **3. Correction** | Développer et tester le correctif | < 1 semaine (selon sévérité) |
| **4. Release** | Publier une release corrective avec tag git | Immédiatement après correction |
| **5. Communication** | Documenter la vulnérabilité dans les release notes | Avec la release |

### 9.3 Notification

| Destinataire | Condition de notification | Canal |
|-------------|--------------------------|-------|
| Utilisateurs GitHub | Vulnérabilité corrigée | Release notes sur GitHub Releases |

Pas d'obligation légale de notification (pas de données personnelles collectées, pas de RGPD applicable).

## 10. Conformité et privacy

Non applicable. Le projet ne collecte, ne stocke et ne transmet aucune donnée personnelle. Aucun cadre réglementaire ne s'applique (SPEC-racine-ApplesoftBasicEmu.md § Contraintes structurantes).

## 11. Spécificités de sécurité

| ID | Exigence | Description | Implémentation | Preuve de conformité | Statut |
|----|----------|-------------|----------------|----------------------|--------|
| SEC-SPE-01 | Protection contre les programmes BASIC adverses | L'émulateur doit résister à des programmes BASIC conçus pour crasher ou exploiter l'interpréteur (lignes surdimensionnées, imbrication profonde, expressions complexes) | Limites documentées : ligne max 239 chars (fidèle Apple II), profondeur de pile bornée, taille fichier < 1 Mo | Fuzzing du Lexer/Parser avec entrées aléatoires, tests avec programmes adverses | ⏳ |
| SEC-SPE-02 | Pas d'accès mémoire Python réelle | PEEK/POKE/CALL n'accèdent qu'à la MemoryMap émulée (bytearray 64 Ko). Ils ne lisent ni n'écrivent jamais la mémoire réelle du processus Python. | MemoryMap est un bytearray isolé. Les adresses sont des indices dans ce tableau, pas des pointeurs mémoire. | Revue de code, tests PEEK/POKE aux limites | ⏳ |

## 12. Légende des statuts

| Statut | Signification |
|--------|---------------|
| ✅ | Implémenté et vérifié |
| 🔄 | En cours d'implémentation |
| ⏳ | Planifié (non démarré) |
| ❌ | Non applicable |
