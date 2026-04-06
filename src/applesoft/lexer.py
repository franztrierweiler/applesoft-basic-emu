"""Lexer Applesoft BASIC — tokenisation gloutonne (RG-0001, RG-0002).

Tokenise une ligne de code source en appliquant la correspondance gloutonne
(longest match) pour les mots réservés, sans exiger de séparateurs.
"""

from __future__ import annotations

from enum import Enum, auto


class TokenType(Enum):
    """Types de tokens Applesoft BASIC."""

    LINENUM = auto()
    KEYWORD = auto()
    IDENT = auto()
    NUMBER = auto()
    STRING = auto()
    OP = auto()
    COLON = auto()  # Séparateur multi-commandes ':'
    SEMICOLON = auto()  # Séparateur PRINT ';'
    COMMA = auto()  # Séparateur ','
    LPAREN = auto()  # '('
    RPAREN = auto()  # ')'
    EOL = auto()  # Fin de ligne


class Token:
    """Un token Applesoft BASIC."""

    __slots__ = ("type", "value")

    def __init__(self, token_type: TokenType, value: object = None):
        self.type = token_type
        self.value = value

    def __repr__(self) -> str:
        if self.value is not None:
            return f"{self.type.name}:{self.value!r}"
        return self.type.name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return NotImplemented
        return self.type == other.type and self.value == other.value


# Mots réservés Applesoft BASIC (GRAMMAR.md § 6.4)
# Triés par longueur décroissante pour la correspondance gloutonne (RG-0002)
KEYWORDS: list[str] = sorted(
    [
        "ABS",
        "AND",
        "ASC",
        "AT",
        "ATN",
        "CALL",
        "CHR$",
        "CLEAR",
        "COLOR=",
        "CONT",
        "COS",
        "DATA",
        "DEF",
        "DEL",
        "DIM",
        "DRAW",
        "END",
        "EXP",
        "FLASH",
        "FN",
        "FOR",
        "GET",
        "GOSUB",
        "GOTO",
        "GR",
        "HCOLOR=",
        "HGR",
        "HGR2",
        "HIMEM:",
        "HOME",
        "HPLOT",
        "HTAB",
        "IF",
        "IN",
        "INPUT",
        "INT",
        "INVERSE",
        "LEFT$",
        "LEN",
        "LET",
        "LIST",
        "LOAD",
        "LOG",
        "LOMEM:",
        "MID$",
        "NEW",
        "NEXT",
        "NORMAL",
        "NOT",
        "ON",
        "ONERR",
        "OR",
        "PEEK",
        "PLOT",
        "POKE",
        "POP",
        "POS",
        "PRINT",
        "READ",
        "REM",
        "RESTORE",
        "RESUME",
        "RETURN",
        "RIGHT$",
        "RND",
        "ROT=",
        "RUN",
        "SAVE",
        "SCALE=",
        "SCRN(",
        "SGN",
        "SIN",
        "SPC(",
        "SPEED=",
        "SQR",
        "STEP",
        "STOP",
        "STR$",
        "TAB(",
        "TAN",
        "TEXT",
        "THEN",
        "TO",
        "VAL",
        "VLIN",
        "VTAB",
        "XDRAW",
    ],
    key=len,
    reverse=True,
)

# Opérateurs multi-caractères, triés par longueur décroissante
OPERATORS: list[str] = ["<>", "><", "<=", "=<", ">=", "=>"]

# Caractères opérateurs simples
SINGLE_OPS: set[str] = {"+", "-", "*", "/", "^", "=", "<", ">"}

# Limite de numéro de ligne (SPEC UC-001)
MAX_LINE_NUMBER = 63999

# Limite de longueur de ligne (UC-001)
MAX_LINE_LENGTH = 239


def tokenize(line: str) -> list[Token]:
    """Tokenise une ligne de code source Applesoft BASIC.

    Applique les règles RG-0001 (tokenisation) et RG-0002 (longest match).
    La ligne est convertie en majuscules (sauf les chaînes).
    """
    # Tronquer à 239 caractères (fidèle Apple II, UC-001)
    if len(line) > MAX_LINE_LENGTH:
        line = line[:MAX_LINE_LENGTH]

    tokens: list[Token] = []
    pos = 0
    length = len(line)

    # Ignorer les espaces initiaux
    pos = _skip_spaces(line, pos, length)

    # Numéro de ligne en tête ?
    if pos < length and line[pos].isdigit():
        num, pos = _read_linenum(line, pos, length)
        tokens.append(Token(TokenType.LINENUM, num))
        pos = _skip_spaces(line, pos, length)

    # Tokeniser le reste de la ligne
    while pos < length:
        ch = line[pos]

        # Espaces : ignorer (RG-0001)
        if ch == " ":
            pos += 1
            continue

        # Chaîne littérale (RG-0005)
        if ch == '"':
            string_val, pos = _read_string(line, pos, length)
            tokens.append(Token(TokenType.STRING, string_val))
            continue

        # REM : tout le reste de la ligne est un commentaire (RG-0009)
        if tokens and tokens[-1].type == TokenType.KEYWORD and tokens[-1].value == "REM":
            # Revenir en arrière — REM a déjà été ajouté, lire le commentaire
            comment = line[pos:]
            tokens.append(Token(TokenType.STRING, comment))
            break

        # Séparateurs et parenthèses
        if ch == ":":
            tokens.append(Token(TokenType.COLON))
            pos += 1
            continue
        if ch == ";":
            tokens.append(Token(TokenType.SEMICOLON))
            pos += 1
            continue
        if ch == ",":
            tokens.append(Token(TokenType.COMMA))
            pos += 1
            continue
        if ch == "(":
            tokens.append(Token(TokenType.LPAREN))
            pos += 1
            continue
        if ch == ")":
            tokens.append(Token(TokenType.RPAREN))
            pos += 1
            continue

        # Nombre (commence par un chiffre ou par '.') (RG-0004)
        if ch.isdigit() or (ch == "." and pos + 1 < length and line[pos + 1].isdigit()):
            num_val, pos = _read_number(line, pos, length)
            tokens.append(Token(TokenType.NUMBER, num_val))
            continue

        # Point seul sans chiffre derrière
        if ch == ".":
            num_val, pos = _read_number(line, pos, length)
            tokens.append(Token(TokenType.NUMBER, num_val))
            continue

        # Opérateurs multi-caractères
        op = _try_read_operator(line, pos, length)
        if op is not None:
            tokens.append(Token(TokenType.OP, op))
            pos += len(op)
            continue

        # Opérateurs simples
        if ch in SINGLE_OPS:
            tokens.append(Token(TokenType.OP, ch))
            pos += 1
            continue

        # '?' est un alias de PRINT (GRAMMAR.md)
        if ch == "?":
            tokens.append(Token(TokenType.KEYWORD, "PRINT"))
            pos += 1
            continue

        # Mots réservés et identifiants (RG-0002 : longest match)
        # À chaque position, on tente d'abord un mot réservé. Si rien ne matche,
        # on accumule un caractère d'identifiant et on recommence.
        if ch.isalpha():
            kw, kw_len = _try_match_keyword(line, pos, length)
            if kw is not None:
                # Émettre l'identifiant accumulé avant le mot-clé
                tokens.append(Token(TokenType.KEYWORD, kw))
                pos += kw_len
            else:
                # Pas de mot-clé → accumuler pour un identifiant
                # Lire un seul caractère alpha/num, puis re-tenter au tour suivant
                ident_chars, pos = _read_ident_until_keyword(line, pos, length)
                tokens.append(Token(TokenType.IDENT, ident_chars))
            continue

        # Caractère non reconnu : ignorer
        pos += 1

    return tokens


def _skip_spaces(line: str, pos: int, length: int) -> int:
    """Avance au-delà des espaces."""
    while pos < length and line[pos] == " ":
        pos += 1
    return pos


def _read_linenum(line: str, pos: int, length: int) -> tuple[int, int]:
    """Lit un numéro de ligne en début de ligne."""
    start = pos
    while pos < length and line[pos].isdigit():
        pos += 1
    return int(line[start:pos]), pos


def _read_string(line: str, pos: int, length: int) -> tuple[str, int]:
    """Lit un littéral chaîne (RG-0005).

    Commence après le guillemet ouvrant. Se termine au prochain guillemet
    ou en fin de ligne (guillemet fermant optionnel).
    """
    pos += 1  # Passer le guillemet ouvrant
    start = pos
    while pos < length and line[pos] != '"':
        pos += 1
    value = line[start:pos]
    if pos < length and line[pos] == '"':
        pos += 1  # Passer le guillemet fermant
    return value, pos


def _read_number(line: str, pos: int, length: int) -> tuple[float, int]:
    """Lit un littéral numérique (RG-0004).

    Supporte : entiers, flottants, notation scientifique.
    """
    start = pos

    # Partie entière
    while pos < length and line[pos].isdigit():
        pos += 1

    # Partie décimale
    if pos < length and line[pos] == ".":
        pos += 1
        while pos < length and line[pos].isdigit():
            pos += 1

    # Notation scientifique
    if pos < length and line[pos].upper() == "E":
        pos += 1
        if pos < length and line[pos] in ("+", "-"):
            pos += 1
        while pos < length and line[pos].isdigit():
            pos += 1

    return float(line[start:pos]), pos


def _try_read_operator(line: str, pos: int, length: int) -> str | None:
    """Essaie de lire un opérateur multi-caractères."""
    remaining = length - pos
    for op in OPERATORS:
        if len(op) <= remaining and line[pos : pos + len(op)] == op:
            return op
    return None


def _try_match_keyword(line: str, pos: int, length: int) -> tuple[str | None, int]:
    """Essaie de matcher un mot réservé par correspondance gloutonne (RG-0002).

    Les mots réservés sont testés du plus long au plus court.
    La comparaison est insensible à la casse.
    """
    upper_line = line.upper()
    remaining = length - pos
    for kw in KEYWORDS:
        kw_len = len(kw)
        if kw_len <= remaining and upper_line[pos : pos + kw_len] == kw:
            return kw, kw_len
    return None, 0


def _read_ident_until_keyword(line: str, pos: int, length: int) -> tuple[str, int]:
    """Lit des caractères d'identifiant jusqu'à ce qu'un mot-clé soit trouvable.

    Le lexer Applesoft vérifie les mots-clés à chaque position (RG-0002).
    On accumule des caractères alphanumériques tant qu'aucun mot-clé ne matche
    à la position courante.
    """
    start = pos

    while pos < length and (line[pos].isalpha() or line[pos].isdigit()):
        pos += 1
        # Vérifier si un mot-clé matche à cette nouvelle position
        if pos < length and line[pos].isalpha():
            kw, _ = _try_match_keyword(line, pos, length)
            if kw is not None:
                break

    raw = line[start:pos].upper()

    # Suffixe $ ou % (seulement s'il n'y a pas de mot-clé juste après)
    if pos < length and line[pos] in ("$", "%"):
        raw += line[pos]
        pos += 1

    # Appliquer la règle des 2 caractères significatifs (RG-0003)
    alpha_num = ""
    for c in raw:
        if c.isalnum():
            alpha_num += c
    suffix = ""
    if raw.endswith("$") or raw.endswith("%"):
        suffix = raw[-1]

    normalized = alpha_num[:2] + suffix
    return normalized, pos
