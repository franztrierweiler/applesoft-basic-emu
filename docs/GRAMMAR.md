# GRAMMAR.md — Grammaire formelle Applesoft BASIC

## Conventions de notation

Ce document utilise la notation EBNF (Extended Backus-Naur Form) avec les conventions suivantes :

| Notation | Signification |
|---|---|
| `=` | Définition |
| `;` | Fin de règle |
| `\|` | Alternative |
| `( ... )` | Groupement |
| `[ ... ]` | Optionnel (0 ou 1 fois) |
| `{ ... }` | Répétition (0 ou N fois) |
| `' ... '` | Terminal littéral (mot-clé ou symbole) |
| `" ... "` | Terminal littéral (chaîne) |
| `(* ... *)` | Commentaire |

Les mots-clés Applesoft sont notés en MAJUSCULES entre apostrophes simples. Les terminaux sont insensibles à la casse en entrée mais stockés en majuscules.

**Important :** En Applesoft BASIC, les espaces sont ignorés en dehors des littéraux chaîne. Les mots-clés n'ont pas besoin de séparateurs (voir EXG-023). Cette grammaire décrit la structure *après* tokenization par le lexer.

---

## 1. Structure du programme

```ebnf
program = { line } ;

line = linenum statement_list NEWLINE ;

linenum = DIGIT { DIGIT } ;
(* Plage valide : 0 à 63999 — voir EXG-002 *)

statement_list = statement { ':' statement } ;
(* Séparateur multi-commandes — voir EXG-010 *)
(* Exception : après REM, le ':' fait partie du commentaire *)

statement = command
          | assignment
          | instruction
          ;
```

---

## 2. Commandes système

```ebnf
command = run_cmd
        | list_cmd
        | new_cmd
        | del_cmd
        | save_cmd
        | load_cmd
        | cont_cmd
        ;

run_cmd  = 'RUN' [ linenum ] ;
(* EXG-003 *)

list_cmd = 'LIST' [ list_range ] ;
list_range = linenum [ '-' [ linenum ] ]
           | '-' linenum
           ;
(* EXG-004 : LIST, LIST n, LIST n-m, LIST -m, LIST n- *)

new_cmd  = 'NEW' ;
(* EXG-005 *)

del_cmd  = 'DEL' linenum ',' linenum ;
(* EXG-006 *)

save_cmd = 'SAVE' string_literal ;
(* EXG-007 *)

load_cmd = 'LOAD' string_literal ;
(* EXG-008 *)

cont_cmd = 'CONT' ;
(* EXG-009 *)
```

---

## 3. Instructions

### 3.1 Assignation

```ebnf
assignment = [ 'LET' ] variable '=' expression ;
(* EXG-029 : LET optionnel *)
```

### 3.2 Entrées / Sorties texte

```ebnf
print_stmt = ( 'PRINT' | '?' ) [ print_list ] ;
(* EXG-011 : '?' est un alias de PRINT *)

print_list = print_item { print_sep print_item } [ print_sep ] ;

print_item = expression
           | spc_call
           | tab_call
           ;

print_sep  = ';'    (* concaténation — voir EXG-011 *)
           | ','    (* tabulation 16 colonnes — voir EXG-011 *)
           ;

spc_call   = 'SPC(' expression ')' ;
(* EXG-015 *)

tab_call   = 'TAB(' expression ')' ;
(* EXG-015 *)

input_stmt = 'INPUT' [ string_literal ';' ] variable_list ;
(* EXG-012 : prompt optionnel *)

variable_list = variable { ',' variable } ;

get_stmt   = 'GET' variable ;
(* EXG-013 *)

data_stmt  = 'DATA' data_item { ',' data_item } ;
(* EXG-014 *)

data_item  = unquoted_datum | string_literal ;

unquoted_datum = { ANY_CHAR_EXCEPT_COMMA_AND_COLON } ;
(* Les données non quotées s'arrêtent à la virgule, au ':' ou à la fin de ligne *)

read_stmt  = 'READ' variable_list ;
(* EXG-014 *)

restore_stmt = 'RESTORE' ;
(* EXG-014 *)
```

### 3.3 Positionnement et affichage

```ebnf
htab_stmt    = 'HTAB' expression ;
(* EXG-016 : colonne 1-40 *)

vtab_stmt    = 'VTAB' expression ;
(* EXG-016 : ligne 1-24 *)

home_stmt    = 'HOME' ;
(* EXG-017 *)

normal_stmt  = 'NORMAL' ;
(* EXG-018 *)

inverse_stmt = 'INVERSE' ;
(* EXG-018 *)

flash_stmt   = 'FLASH' ;
(* EXG-018 *)

speed_stmt   = 'SPEED=' expression ;
(* EXG-020 : 0-255 *)

text_stmt    = 'TEXT' ;
(* EXG-053 *)
```

### 3.4 Commentaire

```ebnf
rem_stmt = 'REM' { ANY_CHAR } ;
(* EXG-019 : tout après REM jusqu'à fin de ligne physique *)
(* Le ':' après REM ne sépare PAS les instructions *)
```

### 3.5 Structures de contrôle

```ebnf
goto_stmt   = 'GOTO' linenum ;
(* EXG-038 *)

gosub_stmt  = 'GOSUB' linenum ;
(* EXG-039 *)

return_stmt = 'RETURN' ;
(* EXG-039 *)

for_stmt    = 'FOR' IDENT '=' expression 'TO' expression [ 'STEP' expression ] ;
(* EXG-040 : variable de contrôle toujours numérique simple *)

next_stmt   = 'NEXT' [ IDENT { ',' IDENT } ] ;
(* EXG-040 : NEXT sans variable = boucle la plus récente *)
(* NEXT I,J équivalent à NEXT I : NEXT J *)

if_stmt     = 'IF' expression 'THEN' then_clause [ 'ELSE' else_clause ] ;
(* EXG-041 *)

then_clause = linenum              (* GOTO implicite *)
            | statement_list       (* une ou plusieurs instructions séparées par ':' *)
            ;

else_clause = linenum              (* GOTO implicite *)
            | statement_list
            ;
(* ELSE appartient au IF le plus récent sur la même ligne *)

on_goto_stmt  = 'ON' expression 'GOTO'  linenum_list ;
(* EXG-042 *)

on_gosub_stmt = 'ON' expression 'GOSUB' linenum_list ;
(* EXG-042 *)

linenum_list  = linenum { ',' linenum } ;

end_stmt    = 'END' ;
(* EXG-043 *)

stop_stmt   = 'STOP' ;
(* EXG-043 *)

pop_stmt    = 'POP' ;
(* EXG-044 *)
```

### 3.6 Gestion d'erreurs

```ebnf
onerr_stmt  = 'ONERR' 'GOTO' linenum ;
(* EXG-046 : ONERR GOTO 0 désactive le gestionnaire *)

resume_stmt = 'RESUME' ;
(* EXG-047 *)
```

### 3.7 Variables et tableaux

```ebnf
dim_stmt = 'DIM' dim_decl { ',' dim_decl } ;
(* EXG-030 *)

dim_decl = IDENT [ '$' | '%' ] '(' expression { ',' expression } ')' ;
(* Indices base 0, jusqu'à 88 dimensions théoriques *)
```

### 3.8 Fonctions utilisateur

```ebnf
def_fn_stmt = 'DEF' 'FN' IDENT [ '$' ] '(' IDENT [ '$' | '%' ] ')' '=' expression ;
(* EXG-037 : un seul paramètre *)
```

### 3.9 Graphisme basse résolution

```ebnf
gr_stmt    = 'GR' ;
(* EXG-048 *)

color_stmt = 'COLOR=' expression ;
(* EXG-049 : 0-15 *)

plot_stmt  = 'PLOT' expression ',' expression ;
(* EXG-050 *)

hlin_stmt  = 'HLIN' expression ',' expression 'AT' expression ;
(* EXG-051 *)

vlin_stmt  = 'VLIN' expression ',' expression 'AT' expression ;
(* EXG-051 *)
```

### 3.10 Graphisme haute résolution

```ebnf
hgr_stmt    = 'HGR' ;
(* EXG-055 *)

hgr2_stmt   = 'HGR2' ;
(* EXG-055 *)

hcolor_stmt = 'HCOLOR=' expression ;
(* EXG-056 : 0-7 *)

hplot_stmt  = 'HPLOT' hplot_args ;
(* EXG-057 *)

hplot_args  = hplot_coord { 'TO' hplot_coord }     (* HPLOT x,y [TO x,y ...] *)
            | 'TO' hplot_coord { 'TO' hplot_coord } (* HPLOT TO x,y — depuis dernière position *)
            ;

hplot_coord = expression ',' expression ;

draw_stmt   = 'DRAW' expression 'AT' expression ',' expression ;
(* EXG-058 *)

xdraw_stmt  = 'XDRAW' expression 'AT' expression ',' expression ;
(* EXG-058 *)

rot_stmt    = 'ROT=' expression ;
(* EXG-059 : 0-255 *)

scale_stmt  = 'SCALE=' expression ;
(* EXG-059 : 0-255 *)
```

### 3.11 Accès mémoire

```ebnf
poke_stmt = 'POKE' expression ',' expression ;
(* EXG-062 : adresse 0-65535, valeur 0-255 *)

call_stmt = 'CALL' expression ;
(* EXG-063 : adresse, -32768 à 65535 *)
```

### 3.12 Récapitulatif des instructions

```ebnf
instruction = print_stmt
            | input_stmt
            | get_stmt
            | data_stmt
            | read_stmt
            | restore_stmt
            | htab_stmt
            | vtab_stmt
            | home_stmt
            | normal_stmt
            | inverse_stmt
            | flash_stmt
            | speed_stmt
            | text_stmt
            | rem_stmt
            | goto_stmt
            | gosub_stmt
            | return_stmt
            | for_stmt
            | next_stmt
            | if_stmt
            | on_goto_stmt
            | on_gosub_stmt
            | end_stmt
            | stop_stmt
            | pop_stmt
            | onerr_stmt
            | resume_stmt
            | dim_stmt
            | def_fn_stmt
            | gr_stmt
            | color_stmt
            | plot_stmt
            | hlin_stmt
            | vlin_stmt
            | hgr_stmt
            | hgr2_stmt
            | hcolor_stmt
            | hplot_stmt
            | draw_stmt
            | xdraw_stmt
            | rot_stmt
            | scale_stmt
            | poke_stmt
            | call_stmt
            ;
```

---

## 4. Expressions

### 4.1 Hiérarchie de précédence

La grammaire encode la précédence des opérateurs par niveaux imbriqués, du plus faible au plus fort.

```ebnf
expression = or_expr ;

or_expr    = and_expr { 'OR' and_expr } ;
(* EXG-033 : précédence la plus faible des opérateurs *)

and_expr   = not_expr { 'AND' not_expr } ;
(* EXG-033 *)

not_expr   = 'NOT' not_expr
           | compare_expr
           ;
(* EXG-033 : NOT est unaire, précédence au-dessus de AND *)

compare_expr = add_expr { compare_op add_expr } ;
(* EXG-032 *)

compare_op = '='
           | '<>'  | '><'
           | '<'   | '>'
           | '<='  | '=<'
           | '>='  | '=>'
           ;
(* EXG-032 : variantes synonymes acceptées *)

add_expr   = mul_expr { ( '+' | '-' ) mul_expr } ;
(* Associativité gauche — EXG-031 *)

mul_expr   = power_expr { ( '*' | '/' ) power_expr } ;
(* Associativité gauche — EXG-031 *)

power_expr = unary_expr [ '^' power_expr ] ;
(* Associativité droite — EXG-031 *)
(* La récursion à droite encode l'associativité droite *)

unary_expr = ( '+' | '-' ) unary_expr
           | primary_expr
           ;
(* EXG-031 : unaire -/+ précédence la plus forte *)
```

### 4.2 Expressions primaires

```ebnf
primary_expr = number_literal
             | string_literal
             | function_call
             | fn_call
             | peek_expr
             | scrn_expr
             | pos_expr
             | variable
             | array_access
             | '(' expression ')'
             ;
```

### 4.3 Accès variables et tableaux

```ebnf
variable     = IDENT [ '$' | '%' ] ;
(* EXG-024 : seuls 2 premiers caractères significatifs *)
(* Suffixes : $ = chaîne, % = entier, rien = flottant *)

array_access = IDENT [ '$' | '%' ] '(' expression { ',' expression } ')' ;
(* EXG-030 : indices base 0 *)
```

---

## 5. Fonctions intégrées

### 5.1 Fonctions mathématiques

```ebnf
function_call = math_func | string_func | conversion_func ;

math_func = 'ABS'  '(' expression ')'
          | 'INT'  '(' expression ')'
          | 'SGN'  '(' expression ')'
          | 'SQR'  '(' expression ')'
          | 'LOG'  '(' expression ')'
          | 'EXP'  '(' expression ')'
          | 'SIN'  '(' expression ')'
          | 'COS'  '(' expression ')'
          | 'TAN'  '(' expression ')'
          | 'ATN'  '(' expression ')'
          | 'RND'  '(' expression ')'
          ;
(* EXG-034, EXG-035 *)
```

### 5.2 Fonctions de chaînes

```ebnf
string_func = 'LEN'    '(' expression ')'
            | 'LEFT$'  '(' expression ',' expression ')'
            | 'RIGHT$' '(' expression ',' expression ')'
            | 'MID$'   '(' expression ',' expression [ ',' expression ] ')'
            | 'ASC'    '(' expression ')'
            | 'CHR$'   '(' expression ')'
            ;
(* EXG-036 *)
```

### 5.3 Fonctions de conversion

```ebnf
conversion_func = 'STR$' '(' expression ')'
                | 'VAL'  '(' expression ')'
                ;
(* EXG-036 *)
```

### 5.4 Fonctions spéciales

```ebnf
fn_call   = 'FN' IDENT [ '$' ] '(' expression ')' ;
(* EXG-037 : appel fonction utilisateur DEF FN *)

peek_expr = 'PEEK' '(' expression ')' ;
(* EXG-061 *)

scrn_expr = 'SCRN(' expression ',' expression ')' ;
(* EXG-052 : noter que SCRN( est un token unique en Applesoft *)

pos_expr  = 'POS' '(' expression ')' ;
(* EXG-021 : argument évalué mais ignoré *)
```

---

## 6. Terminaux lexicaux

### 6.1 Littéraux numériques

```ebnf
number_literal = integer_literal | float_literal ;

integer_literal = DIGIT { DIGIT } ;

float_literal   = DIGIT { DIGIT } '.' { DIGIT } [ exponent ]
                | '.' DIGIT { DIGIT } [ exponent ]
                | DIGIT { DIGIT } exponent
                ;

exponent = 'E' [ '+' | '-' ] DIGIT { DIGIT } ;

DIGIT = '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' ;
```

(* EXG-025 : les nombres négatifs sont exprimés via l'opérateur unaire '-' *)

### 6.2 Littéraux chaîne

```ebnf
string_literal = '"' { STRING_CHAR } ( '"' | END_OF_LINE ) ;
(* EXG-026 : guillemet fermant implicite en fin de ligne *)

STRING_CHAR = ? tout caractère imprimable sauf '"' ? ;
```

### 6.3 Identifiants

```ebnf
IDENT = ALPHA { ALPHA | DIGIT } ;
(* EXG-024 : seuls les 2 premiers caractères sont significatifs *)
(* Les identifiants ne doivent pas correspondre à un mot réservé *)

ALPHA = 'A' | 'B' | ... | 'Z' ;
```

### 6.4 Mots réservés

Liste complète des mots réservés Applesoft BASIC supportés par l'émulateur. Le lexer les reconnaît par correspondance gloutonne (longest match) dans le flux de caractères (voir EXG-023).

```
ABS       AND       ASC       AT        ATN
CALL      CHR$      CLEAR     COLOR=    CONT
COS       DATA      DEF       DEL       DIM
DRAW      END       EXP       FLASH     FN
FOR       GET       GOSUB     GOTO      GR
HCOLOR=   HGR       HGR2      HIMEM:    HOME
HPLOT     HTAB      IF        IN        INPUT
INT       INVERSE   LEFT$     LEN       LET
LIST      LOAD      LOG       LOMEM:    MID$
NEW       NEXT      NORMAL    NOT       ON
ONERR     OR        PEEK      PLOT      POKE
POP       POS       PRINT     READ      REM
RESTORE   RESUME    RETURN    RIGHT$    RND
ROT=      RUN       SAVE      SCALE=    SCRN(
SGN       SIN       SPC(      SPEED=    SQR
STEP      STOP      STR$      TAB(      TAN
TEXT      THEN      TO        VAL       VLIN
VTAB      XDRAW
```

**Notes :**
- `SCRN(`, `SPC(`, `TAB(` incluent la parenthèse ouvrante comme partie du token (convention Applesoft).
- `COLOR=`, `HCOLOR=`, `SPEED=`, `ROT=`, `SCALE=` incluent le signe `=` comme partie du token.
- `HIMEM:` et `LOMEM:` incluent le `:` comme partie du token.
- Le lexer doit tester les mots réservés du plus long au plus court pour garantir la correspondance gloutonne (voir EXG-023).

### 6.5 Opérateurs et séparateurs

```ebnf
operator   = '+' | '-' | '*' | '/' | '^' | '='
           | '<' | '>' | '<>' | '><'
           | '<=' | '=<' | '>=' | '=>'
           ;

separator  = ':' | ';' | ',' | '(' | ')' ;
```

---

## 7. Ordre de précédence des opérateurs (récapitulatif)

Du plus fort au plus faible :

| Niveau | Opérateurs | Associativité | Référence |
|---|---|---|---|
| 1 | Appels de fonctions, `( )` | — | — |
| 2 | Unaire `+`, `-` | Droite | EXG-031 |
| 3 | `^` (exponentiation) | Droite | EXG-031 |
| 4 | `*`, `/` | Gauche | EXG-031 |
| 5 | `+`, `-` (binaires) | Gauche | EXG-031 |
| 6 | `=`, `<>`, `><`, `<`, `>`, `<=`, `=<`, `>=`, `=>` | Gauche | EXG-032 |
| 7 | `NOT` | Droite (unaire) | EXG-033 |
| 8 | `AND` | Gauche | EXG-033 |
| 9 | `OR` | Gauche | EXG-033 |

---

## 8. Règles de tokenization du lexer

Le lexer transforme une ligne source en séquence de tokens avant le parsing. Les règles de tokenization (voir EXG-022, EXG-023) sont :

1. **Espaces ignorés** — Les espaces sont supprimés en dehors des littéraux chaîne.
2. **Littéraux chaîne en premier** — Quand un `"` est rencontré, tout jusqu'au prochain `"` ou fin de ligne est capturé comme token STRING.
3. **Littéraux numériques** — Les séquences de chiffres (avec `.` et `E` optionnels) sont capturées comme token NUMBER.
4. **Mots réservés** — Le lexer tente de reconnaître un mot réservé au début du flux restant, par correspondance gloutonne (longest match). Les mots réservés sont testés du plus long au plus court.
5. **Identifiants** — Si aucun mot réservé ne correspond, une séquence commençant par une lettre est capturée comme IDENT (suivie optionnellement de `$` ou `%`).
6. **Opérateurs et séparateurs** — Les caractères restants sont reconnus comme opérateurs ou séparateurs.
7. **Ligne numérotée** — Si la ligne commence par un nombre, il est capturé comme token LINENUM.

**Exemples de tokenization :**

| Source | Tokens |
|---|---|
| `10 PRINT "HELLO"` | `LINENUM(10)` `KW(PRINT)` `STRING("HELLO")` |
| `FORI=1TO10` | `KW(FOR)` `IDENT(I)` `OP(=)` `NUM(1)` `KW(TO)` `NUM(10)` |
| `IFA>5THENPRINT"OK"` | `KW(IF)` `IDENT(A)` `OP(>)` `NUM(5)` `KW(THEN)` `KW(PRINT)` `STRING("OK")` |
| `SCORE=100` | `IDENT(SC)` `KW(OR)` `IDENT(E)` `OP(=)` `NUM(100)` |

---

## 9. Types de tokens

```ebnf
Token = LINENUM    (* numéro de ligne *)
      | KEYWORD    (* mot réservé Applesoft *)
      | IDENT      (* identifiant variable, 2 caractères significatifs *)
      | NUMBER     (* littéral numérique *)
      | STRING     (* littéral chaîne *)
      | OP         (* opérateur *)
      | SEP        (* séparateur : ; , ( ) *)
      | COLON      (* : séparateur d'instructions *)
      | NEWLINE    (* fin de ligne *)
      ;
```

---

## 10. Correspondance grammaire / exigences

| Production | Exigence(s) |
|---|---|
| `program`, `line`, `statement_list` | EXG-001, EXG-002, EXG-010 |
| `run_cmd` | EXG-003 |
| `list_cmd` | EXG-004 |
| `new_cmd` | EXG-005 |
| `del_cmd` | EXG-006 |
| `save_cmd` | EXG-007 |
| `load_cmd` | EXG-008 |
| `cont_cmd` | EXG-009 |
| `print_stmt`, `spc_call`, `tab_call` | EXG-011, EXG-015 |
| `input_stmt` | EXG-012 |
| `get_stmt` | EXG-013 |
| `data_stmt`, `read_stmt`, `restore_stmt` | EXG-014 |
| `htab_stmt`, `vtab_stmt` | EXG-016 |
| `home_stmt` | EXG-017 |
| `normal_stmt`, `inverse_stmt`, `flash_stmt` | EXG-018 |
| `rem_stmt` | EXG-019 |
| `speed_stmt` | EXG-020 |
| `pos_expr` | EXG-021 |
| Tokenization (section 8) | EXG-022, EXG-023 |
| `IDENT`, `variable` | EXG-024 |
| `number_literal` | EXG-025 |
| `string_literal` | EXG-026 |
| `number_literal` (types runtime) | EXG-027 |
| `string_literal` (types runtime) | EXG-028 |
| `assignment` | EXG-029 |
| `dim_stmt`, `array_access` | EXG-030 |
| `add_expr`, `mul_expr`, `power_expr`, `unary_expr` | EXG-031 |
| `compare_expr`, `compare_op` | EXG-032 |
| `or_expr`, `and_expr`, `not_expr` | EXG-033 |
| `math_func` | EXG-034, EXG-035 |
| `string_func`, `conversion_func` | EXG-036 |
| `def_fn_stmt`, `fn_call` | EXG-037 |
| `goto_stmt` | EXG-038 |
| `gosub_stmt`, `return_stmt` | EXG-039 |
| `for_stmt`, `next_stmt` | EXG-040 |
| `if_stmt`, `then_clause`, `else_clause` | EXG-041 |
| `on_goto_stmt`, `on_gosub_stmt` | EXG-042 |
| `end_stmt`, `stop_stmt` | EXG-043 |
| `pop_stmt` | EXG-044 |
| `onerr_stmt` | EXG-046 |
| `resume_stmt` | EXG-047 |
| `gr_stmt` | EXG-048 |
| `color_stmt` | EXG-049 |
| `plot_stmt` | EXG-050 |
| `hlin_stmt`, `vlin_stmt` | EXG-051 |
| `scrn_expr` | EXG-052 |
| `text_stmt` | EXG-053 |
| `hgr_stmt`, `hgr2_stmt` | EXG-055 |
| `hcolor_stmt` | EXG-056 |
| `hplot_stmt` | EXG-057 |
| `draw_stmt`, `xdraw_stmt` | EXG-058 |
| `rot_stmt`, `scale_stmt` | EXG-059 |
| `peek_expr` | EXG-061 |
| `poke_stmt` | EXG-062 |
| `call_stmt` | EXG-063 |
