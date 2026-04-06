"""Programme Applesoft BASIC en mémoire.

Collection de lignes triées par numéro croissant.
Stocke les tokens et cache l'AST par ligne.
Détokenisation pour LIST et SAVE.
"""

from __future__ import annotations

from .lexer import Token, TokenType


class ProgramLine:
    """Une ligne du programme avec ses tokens et son AST caché."""

    __slots__ = ("number", "tokens", "ast_cache")

    def __init__(self, number: int, tokens: list[Token]):
        self.number = number
        self.tokens = tokens
        self.ast_cache: object | None = None


class Program:
    """Programme Applesoft BASIC en mémoire."""

    def __init__(self):
        self._lines: dict[int, ProgramLine] = {}

    def add_line(self, number: int, tokens: list[Token]) -> None:
        """Ajoute ou remplace une ligne. Invalide le cache AST."""
        self._lines[number] = ProgramLine(number, tokens)

    def delete_line(self, number: int) -> None:
        """Supprime une ligne. Aucune erreur si elle n'existe pas."""
        self._lines.pop(number, None)

    def delete_range(self, start: int, end: int) -> None:
        """Supprime les lignes dont le numéro est entre start et end inclus."""
        to_delete = [n for n in self._lines if start <= n <= end]
        for n in to_delete:
            del self._lines[n]

    def get_line(self, number: int) -> ProgramLine | None:
        """Retourne une ligne ou None."""
        return self._lines.get(number)

    def has_line(self, number: int) -> bool:
        return number in self._lines

    def line_numbers(self) -> list[int]:
        """Retourne les numéros de ligne triés."""
        return sorted(self._lines)

    def get_lines_range(
        self, start: int | None = None, end: int | None = None
    ) -> list[ProgramLine]:
        """Retourne les lignes dans une plage, triées."""
        numbers = sorted(self._lines)
        result = []
        for n in numbers:
            if start is not None and n < start:
                continue
            if end is not None and n > end:
                continue
            result.append(self._lines[n])
        return result

    def next_line_number(self, after: int) -> int | None:
        """Retourne le prochain numéro de ligne après 'after', ou None."""
        numbers = sorted(self._lines)
        for n in numbers:
            if n > after:
                return n
        return None

    def first_line_number(self) -> int | None:
        """Retourne le premier numéro de ligne, ou None si vide."""
        if not self._lines:
            return None
        return min(self._lines)

    def clear(self) -> None:
        """Efface tout le programme."""
        self._lines.clear()

    def is_empty(self) -> bool:
        return len(self._lines) == 0

    def detokenize_line(self, line: ProgramLine) -> str:
        """Détokenise une ligne pour LIST/SAVE."""
        parts = [str(line.number), " "]
        for token in line.tokens:
            parts.append(_token_to_text(token))
        return "".join(parts)

    def detokenize_all(self) -> str:
        """Détokenise tout le programme pour SAVE."""
        lines = []
        for number in sorted(self._lines):
            lines.append(self.detokenize_line(self._lines[number]))
        return "\n".join(lines)

    def cache_ast(self, number: int, ast_node: object) -> None:
        """Met en cache l'AST pour une ligne."""
        line = self._lines.get(number)
        if line is not None:
            line.ast_cache = ast_node

    def get_cached_ast(self, number: int) -> object | None:
        """Retourne l'AST caché ou None."""
        line = self._lines.get(number)
        if line is not None:
            return line.ast_cache
        return None

    def collect_data(self) -> list[tuple[int, list[str]]]:
        """Collecte toutes les instructions DATA du programme.

        Retourne une liste de (numéro_ligne, [valeurs]) dans l'ordre.
        """
        from . import ast_nodes as ast
        from .parser import parse_tokens

        result = []
        for number in sorted(self._lines):
            line = self._lines[number]
            # Parser la ligne pour trouver les DATA
            stmt_list = parse_tokens(line.tokens, number)
            for stmt in stmt_list.statements:
                if isinstance(stmt, ast.DataStmt):
                    result.append((number, stmt.values))
        return result


def _token_to_text(token: Token) -> str:
    """Convertit un token en texte pour la détokenisation."""
    if token.type == TokenType.KEYWORD:
        # Certains mots-clés ont des caractères spéciaux intégrés
        if token.value in _KEYWORDS_NO_SPACE:
            return str(token.value)
        return " " + str(token.value) + " "
    if token.type == TokenType.IDENT:
        return str(token.value)
    if token.type == TokenType.NUMBER:
        val = token.value
        if val == int(val):
            return str(int(val))
        return str(val)
    if token.type == TokenType.STRING:
        return f'"{token.value}"'
    if token.type == TokenType.OP:
        return f" {token.value} "
    if token.type == TokenType.COLON:
        return " : "
    if token.type == TokenType.SEMICOLON:
        return ";"
    if token.type == TokenType.COMMA:
        return ","
    if token.type == TokenType.LPAREN:
        return "("
    if token.type == TokenType.RPAREN:
        return ")"
    return ""


# Mots-clés qui incluent déjà un caractère spécial (pas d'espace supplémentaire)
_KEYWORDS_NO_SPACE = {
    "COLOR=",
    "HCOLOR=",
    "SPEED=",
    "ROT=",
    "SCALE=",
    "SCRN(",
    "SPC(",
    "TAB(",
    "HIMEM:",
    "LOMEM:",
}
