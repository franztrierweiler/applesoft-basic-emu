---
description: Rappel du workflow de développement SDD lors du travail sur le code
paths:
  - "src/**"
  - "tests/**"
---

# Rappel — Workflow de développement SDD

Lors d'un travail structuré sur un EPIC complet (implémentation de fonctionnalités, vérification systématique des AC), suggérer au pilote du projet de lancer `/sdd-dev-workflow <nom-epic>` si ce n'est pas déjà fait.

Ne pas suggérer la commande pour des interventions ponctuelles (correction de bug, refactoring ciblé, ajustement rapide).

## Format de rapport attendu

Chaque itération doit se conclure par un rapport AC :

```
### Statut des critères d'acceptation
- [ ] AC-XXX-XX: Description — Statut + justification
### Prochaines actions
```
