# CLAUDE.md

Ce fichier fournit des instructions à Claude Code (claude.ai/code) pour travailler avec le code de ce dépôt.

## Processus global

```
docs/SPEC.md + fichiers annexes
       |
       v
[1. Spécification]──correction──> 🖊️ sdd-uc-spec-write
       |
       v
[2. Conception technique]───────> 📐 sdd-uc-system-design
       |                            ├─> docs/ARCHITECTURE.md
       |                            ├─> docs/DEPLOYMENT.md
       |                            ├─> docs/SECURITY.md
       |                            └─> docs/COMPLIANCE_MATRIX.md (si réglementaire)
       |
       v
[3. Planification]────────────> 🗺️ /sdd-plan
       |                            └─> plan/<lot>.md
       |
       v
[4. Développement par lot]────> 🏗️ /sdd-dev-workflow <lot>
       |                          (boucle implémentation / AC / tests)
       |
       v
[5. QA par lot]───────────────> 🧪 /sdd-qa-workflow <lot>
       |                          (plan de test, exécution, revue de code)
       |
       v
[6. Livraison]

```

## Vue d'ensemble du projet

Émulateur Applesoft BASIC pour Apple II — projet de démonstration Spec Driven Development (SDD). Toute la documentation est en **français**. Les messages de commit et les commentaires dans le code doivent suivre cette convention.

**Statut :** Spécification v2.0 validée. Conception technique v1.0 validée (ARCHITECTURE, DEPLOYMENT, SECURITY). Prêt pour la planification.

## Structure de la documentation

- `docs/SPEC.md` — Spécification SDD structurée par cas d'utilisation (28 UC, 15 RG, 5 ENF, critères d'acceptation CA-UC-XXX-YY) — v2.0 validée
- `docs/GRAMMAR.md` — Grammaire EBNF complète d'Applesoft BASIC (règles de tokenisation, précédence des opérateurs, toutes les productions)
- `docs/ARCHITECTURE.md` — Architecture détaillée : 14 composants, pipeline Lexer→Parser→Interpreter, architecture en oignon, 6 ADR — v1.0 validée
- `docs/DEPLOYMENT.md` — Déploiement : CLI (script Python) + web (fichier HTML local), releases via tags git — v1.0 validée
- `docs/SECURITY.md` — Sécurité : modèle de menaces, protection contre injection/path traversal/XSS, Brython embarqué — v1.0 validée

Toujours consulter ces documents avant d'implémenter ou de modifier une fonctionnalité. Les cas d'utilisation et exigences ont des niveaux de priorité (Critique, Important, Souhaité) qui guident l'ordre d'implémentation.

La documentation évolue au fur et à mesure des phases d'exécution du projet.

## Méthode de travail pour ce projet

### Travail au sein de l'équipe
1- Le fichier SPEC.md et les fichiers référencés par le fichier SPEC.md constituent les documents de référence. Ils sont utilisés en entrée du skill sdd-uc-system-design lors de la phase de mise au point. Si besoin, le skill sdd-uc-spec-write permet de corriger la spécification et les fichiers qu'elle référence.
2- Le skill sdd-uc-system-design est utilisé pour produire les fichiers de conception technique.
3- La planification est utilisée si et seulement si les fichiers de conception technique sont disponibles.

### Rôle de Claude Code
1- Claude Code agit en tant qu'ingénieur développeur qui collabore étroitement avec la personne qui pilote le projet
2- Non seulement Claude Code produit du code mais il assiste le pilote du projet dans ses tâches de conception et de déroulement du projet
3- Lorsque le pilote du projet propose des solutions techniques, des architectures, Claude Code le "challenge" en ayant en tête toutes les contraintes du projet
4- Claude Code propose des solutions techniques en les éclairant à travers le prisme des coûts de fonctionnement et de la pérennité

## Règles pour Claude Code

### Au démarrage
1- Ce projet suit la méthodologie **Spec Driven Development (SDD)**. Rappeler ce cadre méthodologique à l'utilisateur dès que la session démarre.
2- Inviter systématiquement l'utilisateur à lancer `/sdd-brief` avant toute autre action pour charger le contexte complet du projet.

### En cours d'utilisation
1- A chaque ajout d'un nouveau fichier MD structurant pour le projet, vérifier que CLAUDE.md est bien à jour.
2- Indiquer que le fichier CLAUDE.md a été mis à jour.

### En interaction avec le pilote de projet lors de la phase de conception, de planification, de tests locaux et de déploiement

#### Planification
1- Lors d'une demande de planification, documenter chaque lot dans un fichier spécifique : `plan/<nom-lot>.md` (incluant le numéro du lot)
2- Mettre à jour la progression des tâches dans les fichiers `plan/` correspondants après chaque implémentation
3- Mettre à jour les tableaux d'AC dans les fichiers `plan/` correspondants après chaque implémentation et test unitaire

#### Recettes de test (QA)
Le processus QA est piloté par `/sdd-qa-workflow <lot>`.

#### Commandes
1- Utiliser toujours les commandes Makefile pour les instructions à l'utilisateur (`make test`, `make lint`, `make run`, etc.) plutôt que les commandes brutes (`python`, `pytest`, `ruff`)
2- Le fichier Makefile est la référence pour installer, tester, linter, exécuter, etc
3- Au démarrage, si un Makefile existe, afficher qu'il est disponible avec la commande permettant d'afficher l'aide

### Workflow de développement
Le workflow de développement est piloté par `/sdd-dev-workflow <lot>`.

### Nommage des branches git
1- Développement sur la branche `main` avec Claude Code
2- le pilote du projet donne instruction s'il est nécessaire de "git branch" pour expérimenter sur une branche dédiée
3- Si une autre méthode que celle décrite ici est explicitement utilisée, proposer de basculer la production de code sur une branche expérimentale.

### Commits
1- Ne pas ajouter "Co-Authored-By: Claude" dans les messages de commit
2- Ne pas ajouter "Generated with Claude Code" dans les messages de commit
3- Ne jamais commiter des fichiers qui n'ont pas subi de tests unitaires avec une réussite à 100%
