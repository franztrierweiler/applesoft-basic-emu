# EPIC 02 — Lexer

**Statut :** ⏳ Non démarré
**Priorité :** Critique
**Dépendances :** EPIC 01 (Infrastructure)
**Référence :** ARCHITECTURE.md § 4.1 (Lexer) — GRAMMAR.md § 6, § 8 — SPEC.md EXG-022 à EXG-026

## Objectif

Implémenter le tokenizer Applesoft BASIC : découpage du code source en tokens avec correspondance gloutonne des mots réservés, gestion des espaces ignorés, littéraux numériques et chaînes, identifiants avec suffixe type.

## Tâches

| # | Tâche | Statut |
|---|-------|--------|
| 2.1 | Définir les types `TokenType` (enum) et `Token` (dataclass) dans `tokens.py` | ⏳ |
| 2.2 | Implémenter la table des mots réservés triée par longueur décroissante (longest match) | ⏳ |
| 2.3 | Implémenter la reconnaissance des littéraux chaîne (guillemet fermant optionnel en fin de ligne) | ⏳ |
| 2.4 | Implémenter la reconnaissance des littéraux numériques (entier, flottant, notation scientifique) | ⏳ |
| 2.5 | Implémenter la correspondance gloutonne des mots réservés dans le flux de caractères | ⏳ |
| 2.6 | Implémenter la reconnaissance des identifiants (lettre + alphanum, suffixe `$`/`%`) | ⏳ |
| 2.7 | Implémenter la reconnaissance des opérateurs et séparateurs | ⏳ |
| 2.8 | Implémenter la reconnaissance du numéro de ligne en début de ligne | ⏳ |
| 2.9 | Implémenter la suppression des espaces hors littéraux chaîne | ⏳ |
| 2.10 | Tests unitaires pour tous les CA et CL des exigences couvertes | ⏳ |

## Exigences couvertes

| Exigence | Description | Statut tests |
|----------|-------------|-------------|
| EXG-022 | Tokenization du code source | ⏳ |
| EXG-023 | Correspondance gloutonne des mots réservés | ⏳ |
| EXG-024 | Identifiants — règle des 2 caractères significatifs | ⏳ |
| EXG-025 | Littéraux numériques | ⏳ |
| EXG-026 | Littéraux chaîne | ⏳ |

## Critères d'acceptation (extraits SPEC.md)

| CA | Description | Statut |
|----|-------------|--------|
| CA-022-01 | `10 PRINT "HELLO"` → `[LINENUM:10, KW:PRINT, STRING:"HELLO"]` | ⏳ |
| CA-022-02 | `A = 3.14 + B` → `[IDENT:A, OP:=, NUM:3.14, OP:+, IDENT:B]` | ⏳ |
| CA-022-03 | `10 PRINT"HELLO"` → même résultat que `10 PRINT "HELLO"` | ⏳ |
| CA-023-01 | `10 FORI=1TO10` → `[LINENUM:10, KW:FOR, IDENT:I, OP:=, NUM:1, KW:TO, NUM:10]` | ⏳ |
| CA-023-02 | `10 IFATHENPRINT"OK"` → `[LINENUM:10, KW:IF, IDENT:A, KW:THEN, KW:PRINT, STRING:"OK"]` | ⏳ |
| CA-023-03 | `10 GOTO100` → `[LINENUM:10, KW:GOTO, NUM:100]` | ⏳ |
| CA-025-01 | `X = 3.14` → token NUMBER 3.14 | ⏳ |
| CA-025-02 | `X = 1E3` → token NUMBER 1000 | ⏳ |
| CA-025-03 | `X = .5` → token NUMBER 0.5 | ⏳ |
| CA-026-01 | `PRINT "HELLO WORLD"` → STRING "HELLO WORLD" | ⏳ |
| CA-026-02 | `PRINT "HELLO` → STRING "HELLO" (guillemet implicite) | ⏳ |

## Cas limites à tester

| CL | Description | Statut |
|----|-------------|--------|
| CL-022-01 | Ligne vide → séquence vide | ⏳ |
| CL-022-02 | Chaîne non fermée → guillemet implicite fin de ligne | ⏳ |
| CL-023-01 | `SCORE` → `[IDENT:SC, KW:OR, IDENT:E]` | ⏳ |
| CL-023-02 | `NOTATION` → correspondance gloutonne NOT/AT/ION | ⏳ |
| CL-025-01 | `1E40` → token NUMBER avec représentation textuelle | ⏳ |
| CL-025-02 | `10.5.3` → deux tokens NUMBER: 10.5 et .3 | ⏳ |
| CL-026-01 | `""` → STRING vide | ⏳ |

## Livrables

- `src/tokens.py` — types Token et TokenType
- `src/lexer.py` — tokenizer complet
- `tests/unit/test_lexer.py` — tests exhaustifs
