# Initialisation du projet

## Instructions

1. Lire tous les fichiers markdown dans le répertoire `docs/`
2. Lire le fichier `CLAUDE.md` à la racine du projet
3. Si un fichier `Makefile` existe, afficher : "Makefile disponible — `make help` pour l'aide"
4. Lister les commandes SDD disponibles (fichiers `sdd-*` dans `.claude/commands/` du projet) dans un tableau avec une synthèse de 10 mots pour chacune.
5. Lister les skills SDD disponibles (skills système dont le nom commence par `sdd-` listés dans le system-reminder, **hors** ceux déjà listés comme commandes à l'étape 4) dans un tableau séparé avec une synthèse de 10 mots pour chacun.
6. Afficher le statut actuel du projet (extrait de CLAUDE.md)
7. Si des fichiers `plan/*.md` existent, afficher la liste des EPICs et leur progression
8. Terminer par : "Prêt. Quelle est la prochaine étape ?"
