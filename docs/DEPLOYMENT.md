# AppleSoft BASIC Emulator — Déploiement

Version : 1.0
Date : 2026-04-06
Auteur : Franz / Claude
Statut : Validé
Spec de référence : SPEC-racine-ApplesoftBasicEmu.md v3.1
Architecture de référence : ARCHITECTURE.md v1.0

## 1. Vue d'ensemble du déploiement

L'émulateur Applesoft BASIC se déploie de deux manières, correspondant aux deux phases du projet. La Phase 1 (CLI) est un script Python à copier et exécuter localement. La Phase 2 (web) est un ensemble de fichiers statiques (HTML + CSS + Python Brython) à ouvrir directement dans un navigateur, sans serveur. Il n'y a aucune infrastructure à provisionner, aucun service à opérer, aucun secret à gérer. Les mises à jour sont distribuées via des tags git et releases GitHub.

**Type de solution :** CLI (Phase 1) + Application web locale (Phase 2)

## 2. Prérequis

### 2.1 Prérequis infrastructure

| Prérequis | Spécification | Obligatoire | Notes |
|-----------|--------------|-------------|-------|
| Machine utilisateur | Tout OS supportant Python 3.10+ (Linux, macOS, Windows) | Oui | Phase 1 |
| Navigateur web moderne | Chrome 90+, Firefox 88+, Safari 15+, Edge 90+ | Phase 2 uniquement | Doit supporter ES6, Canvas API, localStorage |
| Terminal avec support ANSI | Tout terminal moderne (GNOME Terminal, iTerm2, Windows Terminal) | Phase 1 uniquement | Pour le rendu graphique en couleur. Voir ARCHITECTURE.md ADR-004 |

### 2.2 Prérequis logiciels

| Logiciel | Version minimale | Rôle | Installation |
|----------|-----------------|------|-------------|
| Python | 3.10.12+ | Exécution de l'interpréteur CLI | `apt install python3` / `brew install python` / python.org |
| pip | Dernière stable | Installation des dépendances dev | Inclus avec Python |
| Pillow | Dernière stable | Export PNG des graphiques (optionnel) | `pip install Pillow` |
| pytest | Dernière stable | Exécution des tests (dev uniquement) | `pip install pytest` |
| ruff | Dernière stable | Lint et formatage (dev uniquement) | `pip install ruff` |
| make | Toute version | Exécution des commandes projet | Préinstallé Linux/macOS, `choco install make` Windows |
| git | 2.30+ | Gestion de version, récupération du code | Préinstallé ou via gestionnaire de paquets |

### 2.3 Prérequis réseau

Aucun. L'émulateur fonctionne entièrement hors ligne. La seule connexion réseau nécessaire est pour le clonage initial du dépôt et l'installation des dépendances pip.

### 2.4 Prérequis secrets et credentials

Aucun. Le projet n'utilise aucun secret, aucune clé API, aucun certificat.

## 3. Environnements

| Environnement | Usage | Infra | Données | Accès |
|--------------|-------|-------|---------|-------|
| dev | Développement et tests | Machine locale du pilote | Programmes BASIC d'exemple et de test (`examples/`, `tests/fixtures/`) | Pilote + Claude Code |
| utilisateur | Utilisation finale | Machine de l'utilisateur | Programmes BASIC de l'utilisateur (fichiers .bas) | Utilisateur |

Il n'y a pas d'environnement staging ni production au sens classique. Le livrable est distribué directement à l'utilisateur via une release GitHub.

## 4. Configuration par environnement

| Variable | Description | Dev | Utilisateur | Obligatoire |
|----------|-------------|-----|-------------|-------------|
| `--debug` | Active le mode debug (trace d'exécution) | Fréquemment utilisé | À la demande | Non |
| Pillow installé | Permet l'export PNG | Oui | Optionnel | Non |

L'émulateur ne nécessite aucun fichier de configuration. Tout le paramétrage se fait via les arguments CLI ou les commandes REPL (`DEBUG ON`/`DEBUG OFF`).

## 5. Procédure de build

### 5.1 Build Phase 1 (CLI)

Aucun build nécessaire. Le code Python est exécuté directement.

```bash
# Installation des dépendances dev
make install

# Vérification
make test
make lint
```

### 5.2 Build Phase 2 (Web)

Aucun build nécessaire. Les fichiers HTML, CSS et Python sont servis tels quels. Brython est chargé depuis un CDN ou inclus localement dans `web/`.

### 5.3 Artefacts produits

| Artefact | Type | Destination | Taille estimée |
|----------|------|-------------|---------------|
| Dépôt git complet | Répertoire de fichiers | Machine utilisateur | ~1 Mo (sans .git) |
| Release GitHub (.tar.gz / .zip) | Archive | GitHub Releases | ~500 Ko |

## 6. Procédure de déploiement

### 6.1 Premier déploiement (installation initiale)

**Phase 1 — CLI :**

```bash
# 1. Cloner le dépôt
git clone https://github.com/<owner>/applesoft-basic-emu.git
cd applesoft-basic-emu

# 2. (Optionnel) Installer Pillow pour l'export PNG
pip install Pillow

# 3. Lancer l'émulateur
python -m applesoft

# 4. (Optionnel) Exécuter un fichier .bas directement
python -m applesoft examples/hello.bas
```

**Phase 2 — Web :**

```bash
# 1. Ouvrir le fichier HTML directement dans le navigateur
# Depuis le répertoire du projet :
open web/index.html          # macOS
xdg-open web/index.html      # Linux
start web/index.html          # Windows
```

Aucune initialisation de données nécessaire. Les tables de données (mots réservés, codes d'erreur, adresses mémoire, palettes de couleurs) sont embarquées en constantes dans le code (voir ARCHITECTURE.md § 4.7).

### 6.2 Mise à jour (déploiement courant)

**Stratégie :** Manuelle (pull git ou téléchargement de release)

```bash
# Option A : via git
git pull origin main

# Option B : via release GitHub
# Télécharger la dernière release depuis GitHub Releases
# Extraire et remplacer le répertoire existant
```

Aucune migration de données nécessaire entre versions. Les fichiers .bas de l'utilisateur sont indépendants du code de l'émulateur.

### 6.3 Rollback

```bash
# Revenir à une version spécifique via git tag
git checkout v<version>
```

**Temps estimé de rollback :** Immédiat (< 10 secondes).

## 7. Pipeline CI/CD

Pas de pipeline CI/CD automatisé. Le pilote exécute manuellement les commandes de qualité avant chaque release :

```bash
make lint     # Vérification du style et des erreurs
make test     # Exécution des tests unitaires et d'intégration
```

**Procédure de release :**

```bash
# 1. S'assurer que tous les tests passent
make test
make lint

# 2. Créer le tag
git tag -a v<X.Y.Z> -m "Description de la release"

# 3. Pousser le tag
git push origin v<X.Y.Z>

# 4. Créer la release GitHub (via gh CLI ou interface web)
gh release create v<X.Y.Z> --title "v<X.Y.Z> — Titre" --notes "Description"
```

**Convention de versioning (Semantic Versioning) :**

| Type | Incrémentation | Exemple |
|------|---------------|---------|
| Correctif | Patch (X.Y.**Z**) | Correction de bug, fix d'un CA |
| Nouvelle fonctionnalité | Minor (X.**Y**.0) | Ajout d'un UC complet |
| Changement majeur | Major (**X**.0.0) | Phase 2, changement d'architecture |

## 8. Health checks et readiness

Le système étant un script local sans composant serveur, les health checks classiques (endpoints HTTP) ne s'appliquent pas.

| Mécanisme | Type | Vérifications | Résultat OK | Résultat KO |
|-----------|------|---------------|------------|------------|
| `python -m applesoft --version` | Smoke test CLI | Le module s'importe et affiche la version | Version affichée | ImportError ou crash |
| `make test` | Tests automatisés | Tous les tests passent | Exit code 0 | Exit code non-0 |
| Ouverture `web/index.html` | Smoke test web | Le prompt `]` apparaît dans la console | Prompt visible | Erreur Brython affichée |

**Critères de readiness pour une release :**

- [ ] `make lint` passe sans erreur
- [ ] `make test` passe à 100%
- [ ] `python -m applesoft --version` affiche la version correcte
- [ ] Les programmes d'exemple (`examples/*.bas`) s'exécutent correctement
- [ ] (Phase 2) `web/index.html` s'ouvre et le prompt `]` apparaît

## 9. Monitoring et observabilité

### 9.1 Métriques

Pas de monitoring en production. Le mode debug intégré (voir ARCHITECTURE.md ADR-006) fournit l'observabilité nécessaire pour le développement et le diagnostic :

| Mécanisme | Activation | Information fournie |
|-----------|-----------|-------------------|
| `--debug` / `DEBUG ON` | Flag CLI ou commande REPL | Ligne courante, instruction exécutée, état des variables |
| Sortie d'erreur standard | Automatique | Messages d'erreur Applesoft (RG-0010) |

### 9.2 Logs

Pas de système de logs structurés. Les erreurs sont affichées directement à l'utilisateur via les messages Applesoft (`?MESSAGE ERROR [IN linenum]`). Le mode debug produit une trace sur la sortie standard.

### 9.3 Alertes

Non applicable. Application locale mono-utilisateur.

## 10. Sauvegarde et restauration

| Donnée | Méthode | Fréquence | Rétention | Restauration |
|--------|---------|-----------|-----------|-------------|
| Code source | Git (dépôt distant GitHub) | À chaque commit/push | Historique complet | `git clone` ou `git checkout` |
| Programmes utilisateur (.bas) | Responsabilité de l'utilisateur | À sa discrétion | — | Copie manuelle des fichiers .bas |
| localStorage (Phase 2) | Natif navigateur | Automatique | Jusqu'à effacement du cache | Non récupérable si le cache est vidé |

**Recommandation à l'utilisateur :** Les programmes importants doivent être sauvegardés en fichiers .bas via `SAVE "nom.bas"` (CLI) ou le bouton Export (Phase 2). Le localStorage du navigateur n'est pas un stockage pérenne.

## 11. Disaster recovery

Le projet étant une application locale sans infrastructure, les scénarios de disaster recovery classiques ne s'appliquent pas.

| Scénario | Impact | Procédure de reprise | Responsable |
|----------|--------|---------------------|-------------|
| Perte du poste de développement | Perte du travail non poussé | Cloner depuis GitHub, reprendre au dernier commit | Pilote |
| Corruption du dépôt local | Code source inaccessible | `git clone` depuis GitHub | Pilote |
| Perte de programmes .bas utilisateur | Programmes perdus | Restauration depuis backup utilisateur (si existant) | Utilisateur |
| Vidage localStorage (Phase 2) | Programmes web perdus | Non récupérable — d'où la recommandation d'export .bas | Utilisateur |

**RPO / RTO :**

| Métrique | Objectif | Mécanisme |
|----------|---------|-----------|
| RPO (perte de données max) | Dernier `git push` | Commits réguliers et push fréquents |
| RTO (temps de reprise max) | < 5 minutes | `git clone` + `pip install Pillow` (optionnel) |
