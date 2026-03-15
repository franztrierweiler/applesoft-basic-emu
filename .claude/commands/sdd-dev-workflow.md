# Workflow de développement d'un EPIC

## Argument

$ARGUMENTS — nom de l'EPIC (ex: `epic-01-lexer`)

## Instructions

### 1. Chargement du contexte

1. Lire le fichier `plan/$ARGUMENTS.md`
2. Lire les critères d'acceptation (AC) listés dans le plan
3. Lire les contraintes techniques mentionnées
4. Lire les exigences, règles et bonnes pratiques de sécurité dans `docs/SPEC.md`
5. Afficher un résumé : nom de l'EPIC, nombre de fonctionnalités, nombre d'AC

### 2. Boucle d'implémentation

Pour chaque fonctionnalité de l'EPIC :

1. Implémenter une première version minimale
2. Expliquer ce qu'a fait l'itération en quelques lignes, en indiquant "Fin d'itération, voici le résultat"
3. Vérifier chaque critère d'acceptation (AC) un par un
4. Lister explicitement : ✅ AC satisfait / ❌ AC non satisfait
5. Si des AC ne sont pas satisfaits, itérer jusqu'à ce que tous soient validés

### 3. Vérification globale

Après chaque implémentation significative :

1. Exécuter les tests unitaires associés (via Makefile)
2. Exécuter les tests d'intégration si pertinents
3. Revoir le code avec pour référence les AC de l'EPIC
4. Revoir le code avec pour référence les règles de sécurité et les règles de codage
5. Remplir la matrice de conformité si pertinent
6. Pour chaque AC, démontrer concrètement qu'il est satisfait (test, exemple, preuve)
7. Si un AC n'est pas vérifiable automatiquement, expliquer comment le valider manuellement
8. Indiquer "Fin d'implémentation significative, voici le résultat"

### 4. Rapport

Produire un rapport au format suivant :

```
### Statut des critères d'acceptation — $ARGUMENTS
- [ ] AC-XXX-XX: Description — Statut + justification
- [ ] AC-XXX-XX: Description — Statut + justification
### Prochaines actions
```

### 5. Mise à jour du plan

1. Mettre à jour la progression dans `plan/$ARGUMENTS.md`
2. Mettre à jour les tableaux d'AC dans `plan/$ARGUMENTS.md`

### 6. Clôture

Si tous les AC sont à 100% :
1. Indiquer "EPIC $ARGUMENTS — tous les AC sont satisfaits"
2. Demander au pilote du projet s'il souhaite lancer la QA : `/sdd-qa-workflow $ARGUMENTS`
