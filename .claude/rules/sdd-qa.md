---
description: Rappel du processus QA SDD lors du travail sur les fichiers de recette
paths:
  - "qa/**"
---

# Rappel — Processus QA SDD

Lors d'un travail structuré de recette de test sur un EPIC complet, suggérer au pilote du projet de lancer `/sdd-qa-workflow <nom-epic>` si ce n'est pas déjà fait.

Ne pas suggérer la commande pour des consultations ou modifications ponctuelles de fichiers QA.

## Conventions QA

- Plans de test : `qa/plan-test-<nom-epic>.md`
- Rapports de revue : `qa/reviews/<nom-epic>-review.md`
- La QA ne s'exécute que sur un EPIC complet, testé unitairement et avec des AC à 100%
