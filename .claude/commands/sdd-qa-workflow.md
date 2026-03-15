# Recette de test (QA) d'un EPIC

## Argument

$ARGUMENTS — nom de l'EPIC (ex: `epic-01-lexer`)

## Prérequis

- L'EPIC doit être complet, testé unitairement et avec des AC à 100%
- Si ce n'est pas le cas, indiquer les AC manquants et suggérer `/sdd-dev-workflow $ARGUMENTS`

## Instructions

### 1. Chargement du contexte

1. Lire le fichier `plan/$ARGUMENTS.md`
2. Lire les AC et leurs justifications de satisfaction
3. Lire les fichiers source implémentés pour cet EPIC
4. Lire les tests unitaires existants

### 2. Élaboration du plan de test

1. Produire le plan de test dans `qa/plan-test-$ARGUMENTS.md`
2. Pour chaque AC, définir :
   - Scénarios de test nominaux
   - Scénarios de test aux limites (basés sur les CL-XXX-XX de la spec)
   - Scénarios de test en erreur
3. Identifier les tests manuels nécessaires (si applicable)
4. Soumettre le plan de test au pilote du projet pour validation

### 3. Exécution de la recette

Après validation du plan par le pilote :

1. Exécuter les tests via Makefile
2. Pour chaque scénario :
   - Résultat : ✅ Passé / ❌ Échoué
   - Si échoué : description du problème, impact, suggestion de correction
3. Indiquer "Fin de la recette de test, voici le résultat"

### 4. Revue de code

1. Effectuer une revue de code de l'EPIC
2. Vérifier : lisibilité, sécurité, performance, conformité aux conventions
3. Produire le rapport de revue dans `qa/code-review/$ARGUMENTS-review.md`

### 5. Rapport final

Produire le rapport final dans `qa/qa-results/rapport-$ARGUMENTS.md` avec le contenu suivant :

```markdown
# Rapport QA — EPIC [numéro] [nom]

**Date :** [YYYY-MM-DD]
**EPIC :** $ARGUMENTS
**Verdict :** ✅ VALIDÉ / ❌ À CORRIGER

## Résultats

- Tests unitaires : X/Y passés
- Tests d'intégration : X/Y passés (ou N/A)
- Scénarios QA : X/Y passés
- Revue de code : OK / points à corriger

## Détail des scénarios

| # | Scénario | Résultat |
|---|----------|----------|
| ... | ... | ✅ / ❌ |

## Points d'attention

[Points mineurs ou avertissements]

## Références

- Plan de test : `qa/plan-test-$ARGUMENTS.md`
- Revue de code : `qa/code-review/$ARGUMENTS-review.md`
```

### 6. Clôture

Si le verdict est VALIDÉ :
1. Indiquer "QA $ARGUMENTS — validé, prêt pour commit"
2. Attendre l'instruction du pilote pour le commit
