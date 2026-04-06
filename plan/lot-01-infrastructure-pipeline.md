# Lot 1 — Infrastructure et pipeline de base

## Objectif

Mettre en place les fondations du projet : structure de répertoire, outillage (Makefile, pytest, ruff), et le pipeline complet Lexer → Parser → Program. Le REPL est fonctionnel avec le prompt `]`, la distinction mode direct / mode différé, et les commandes de gestion du programme (LIST, NEW, DEL). Après ce lot, on peut saisir des lignes, les stocker, les lister et les supprimer.

## UC couverts

| UC | Intitulé | Priorité |
|---|---|---|
| UC-001 | Interagir via le REPL | Critique |
| UC-002 | Gérer le programme en mémoire | Critique |

## Composants impactés

| Composant | Rôle dans ce lot |
|---|---|
| Lexer (`lexer.py`) | Implémentation complète : tokenisation gloutonne (RG-0001, RG-0002), reconnaissance des mots réservés, identifiants (RG-0003), littéraux numériques (RG-0004), littéraux chaîne (RG-0005) |
| Parser (`parser.py`) | Implémentation complète : recursive descent, 9 niveaux de précédence, toutes les productions de GRAMMAR.md. L'AST est produit mais pas encore exécuté (lot 2). |
| Program (`program.py`) | Collection de lignes triées par numéro. Stockage tokens + cache AST. Détokenisation pour LIST. |
| ErrorHandler (`errors.py`) | Table des 17 codes d'erreur Applesoft (RG-0010). Formatage des messages. |
| NumberFormatter (`formatter.py`) | Formatage des nombres selon les conventions Applesoft (RG-0006). |
| IOBridge (`io_bridge.py`) | Interface abstraite d'I/O (protocole Python). |
| IOBridgeCLI (`io_cli.py`) | Implémentation CLI basique : stdin/stdout, prompt. |
| REPL (`repl.py`) | Boucle interactive : prompt `]`, dispatch mode direct/différé, commandes LIST, NEW, DEL. |
| `__main__.py` | Point d'entrée `python -m applesoft`. |

## Dépendances

- Aucune (premier lot)

## Fonctionnalités

### F1 — Structure du projet et outillage

Création de la structure de répertoire conforme à ARCHITECTURE.md § 7 :
- `src/applesoft/` avec tous les modules
- `tests/unit/` avec les fichiers de test
- `Makefile` avec cibles : `install`, `test`, `lint`, `run`
- `pyproject.toml` avec configuration pytest et ruff

### F2 — Lexer complet

Tokenisation complète d'une ligne Applesoft BASIC :
- Reconnaissance des mots réservés par correspondance gloutonne (longest match, RG-0002)
- Mots réservés triés par longueur décroissante
- Identifiants (2 caractères significatifs, suffixe $/%  — RG-0003)
- Littéraux numériques (entiers, flottants, notation scientifique — RG-0004)
- Littéraux chaîne (guillemet fermant optionnel — RG-0005)
- Opérateurs et séparateurs
- Numéros de ligne
- Espaces ignorés hors chaînes (RG-0001)

### F3 — Parser complet

Construction de l'AST à partir des tokens :
- Recursive descent avec 9 niveaux de précédence (GRAMMAR.md § 7)
- Toutes les productions de la grammaire (commandes, instructions, expressions)
- Nœuds AST typés pour chaque construction du langage
- Messages d'erreur Applesoft en cas d'erreur de syntaxe (RG-0010)

### F4 — Program (gestion du programme en mémoire)

- Stockage de lignes triées par numéro croissant
- Ajout / remplacement / suppression de lignes
- Détokenisation pour LIST et SAVE
- Cache AST par ligne (invalidé à la modification)

### F5 — REPL et commandes de gestion

- Boucle interactive avec prompt `]`
- Mode différé : saisie d'une ligne numérotée → tokenisation → stockage dans Program
- Mode direct : saisie sans numéro → tokenisation → parsing (exécution au lot 2)
- Commande LIST : affichage du programme (détokenisation)
- Commande NEW : effacement du programme
- Commande DEL : suppression d'une plage de lignes
- Ligne numérotée seule → suppression de la ligne
- Ligne vide → prompt réaffiché
- Ligne > 239 caractères → tronquée (fidèle Apple II)
- Numéro de ligne > 63999 → `?SYNTAX ERROR`

### F6 — ErrorHandler et NumberFormatter

- Table des 17 codes d'erreur avec messages (RG-0010)
- Format `?MESSAGE ERROR [IN linenum]`
- Formatage des nombres : espace pour positif, pas de zéros inutiles, notation scientifique > 9 chiffres (RG-0006)

## Critères d'acceptation

| AC | Description | Statut | Justification | Date |
|---|---|---|---|---|
| CA-RG-0001-01 | `10 PRINT "HELLO"` → tokens `[LINENUM:10, KW:PRINT, STR:"HELLO"]` | ✅ | test_ca_rg_0001_01_print_hello | 2026-04-06 |
| CA-RG-0001-02 | `A = 3.14 + B` → tokens `[IDENT:A, OP:=, NUM:3.14, OP:+, IDENT:B]` | ✅ | test_ca_rg_0001_02_expression | 2026-04-06 |
| CA-RG-0001-03 | `10 PRINT"HELLO"` → même résultat que `10 PRINT "HELLO"` | ✅ | test_ca_rg_0001_03_no_space_between_keyword_and_string | 2026-04-06 |
| CA-RG-0001-04 | Ligne vide → séquence vide ou token fin de ligne | ✅ | test_ca_rg_0001_04_empty_line | 2026-04-06 |
| CA-RG-0001-05 | `10 PRINT "HELLO` (non fermée) → chaîne terminée en fin de ligne | ✅ | test_ca_rg_0001_05_unclosed_string | 2026-04-06 |
| CA-RG-0002-01 | `10 FORI=1TO10` → `[LINENUM:10, KW:FOR, IDENT:I, OP:=, NUM:1, KW:TO, NUM:10]` | ✅ | test_ca_rg_0002_01_for_i | 2026-04-06 |
| CA-RG-0002-02 | `10 IFATHENPRINT"OK"` → `[LINENUM:10, KW:IF, KW:AT, IDENT:HEN, KW:PRINT, STR:"OK"]` | ✅ | test_ca_rg_0002_02_if_at_hen | 2026-04-06 |
| CA-RG-0002-03 | `10 GOTO100` → `[LINENUM:10, KW:GOTO, NUM:100]` | ✅ | test_ca_rg_0002_03_goto_100 | 2026-04-06 |
| CA-RG-0002-04 | `SCORE` → `[IDENT:SC, KW:OR, IDENT:E]` | ✅ | test_ca_rg_0002_04_score | 2026-04-06 |
| CA-RG-0002-05 | `NOTATION` → `[KW:NOT, KW:AT, IDENT:I, KW:ON]` | ✅ | test_ca_rg_0002_05_notation | 2026-04-06 |
| CA-RG-0003-01 | LOW et LOSS sont la même variable (2 chars significatifs) | ✅ | test_ca_rg_0003_01_two_char_significance | 2026-04-06 |
| CA-RG-0003-02 | A, A$, A% sont trois variables distinctes | ✅ | test_ca_rg_0003_02_distinct_suffixes | 2026-04-06 |
| CA-RG-0004-01 | `X = 3.14` → token NUMBER valeur 3.14 | ✅ | test_ca_rg_0004_01_float | 2026-04-06 |
| CA-RG-0004-02 | `X = 1E3` → token NUMBER valeur 1000 | ✅ | test_ca_rg_0004_02_scientific | 2026-04-06 |
| CA-RG-0004-03 | `X = .5` → token NUMBER valeur 0.5 | ✅ | test_ca_rg_0004_03_dot_prefix | 2026-04-06 |
| CA-RG-0005-01 | `PRINT "HELLO WORLD"` → token STRING `HELLO WORLD` | ✅ | test_ca_rg_0005_01_normal_string | 2026-04-06 |
| CA-RG-0005-02 | `PRINT "HELLO` → token STRING `HELLO` (fermant implicite) | ✅ | test_ca_rg_0005_02_unclosed_string | 2026-04-06 |
| CA-RG-0005-03 | `""` → token STRING vide | ✅ | test_ca_rg_0005_03_empty_string | 2026-04-06 |
| CA-RG-0006-01 | `PRINT 3.14` → ` 3.14` (espace pour positif) | ✅ | test_ca_rg_0006_01_positive_float | 2026-04-06 |
| CA-RG-0006-02 | `PRINT -5` → `-5` (pas d'espace) | ✅ | test_ca_rg_0006_02_negative_integer | 2026-04-06 |
| CA-RG-0006-03 | `PRINT 1000000000` → ` 1E+09` | ✅ | test_ca_rg_0006_03_scientific_notation | 2026-04-06 |
| CA-RG-0010-01 | `10 X=1/0` via RUN → `?DIVISION BY ZERO ERROR IN 10` | ✅ | test_ca_rg_0010_01_error_with_line_number | 2026-04-06 |
| CA-RG-0010-02 | `X=1/0` mode direct → `?DIVISION BY ZERO ERROR` (sans numéro) | ✅ | test_ca_rg_0010_02_error_without_line_number | 2026-04-06 |
| CA-UC-001-01 | Émulateur démarré → prompt `]` affiché | ✅ | test_ca_uc_001_01_prompt_displayed | 2026-04-06 |
| CA-UC-001-03 | `10 PRINT "HELLO"` → stocké en mémoire sans exécution | ✅ | test_ca_uc_001_03_store_line | 2026-04-06 |
| CA-UC-001-04 | `20 PRINT "B"` puis `10 PRINT "A"` → ordre 10, 20 | ✅ | test_ca_uc_001_04_sorted_order | 2026-04-06 |
| CA-UC-001-05 | `10 PRINT "Z"` remplace une ligne 10 existante | ✅ | test_ca_uc_001_05_replace_line | 2026-04-06 |
| CA-UC-001-06 | `10` seul → supprime la ligne 10 | ✅ | test_ca_uc_001_06_delete_by_number | 2026-04-06 |
| CA-UC-002-01 | LIST → affiche les lignes dans l'ordre | ✅ | test_ca_uc_002_01_list_all | 2026-04-06 |
| CA-UC-002-02 | `LIST 20` → affiche uniquement la ligne 20 | ✅ | test_ca_uc_002_02_list_single | 2026-04-06 |
| CA-UC-002-03 | `LIST 10,20` → affiche les lignes 10 à 20 | ✅ | test_ca_uc_002_03_list_range | 2026-04-06 |
| CA-UC-002-04 | NEW → LIST n'affiche rien | ✅ | test_ca_uc_002_04_new | 2026-04-06 |
| CA-UC-002-05 | `DEL 10,20` → supprime les lignes 10 à 20 | ✅ | test_ca_uc_002_05_del_range | 2026-04-06 |
| CA-UC-002-06 | `DEL 20,20` → supprime uniquement la ligne 20 | ✅ | test_ca_uc_002_06_del_single | 2026-04-06 |

## Prochaines actions

Lot terminé — prêt pour QA
