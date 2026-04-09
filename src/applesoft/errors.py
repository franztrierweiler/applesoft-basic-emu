"""Gestionnaire d'erreurs Applesoft BASIC (RG-0010).

Table des 17 codes d'erreur avec messages fidèles à l'Apple II.
Format : ?MESSAGE ERROR [IN linenum]
"""

# Table des codes d'erreur Applesoft (RG-0010)
ERROR_MESSAGES: dict[int, str] = {
    0: "NEXT WITHOUT FOR",
    16: "SYNTAX",
    22: "RETURN WITHOUT GOSUB",
    42: "OUT OF DATA",
    53: "ILLEGAL QUANTITY",
    69: "OVERFLOW",
    77: "OUT OF MEMORY",
    90: "UNDEF'D STATEMENT",
    107: "BAD SUBSCRIPT",
    120: "REDIM'D ARRAY",
    133: "DIVISION BY ZERO",
    163: "TYPE MISMATCH",
    176: "STRING TOO LONG",
    224: "UNDEF'D FUNCTION",
    254: "CAN'T CONTINUE",
    255: "FORMULA TOO COMPLEX",
    # Codes étendus pour fichiers (UC-004, UC-005)
    256: "FILE NOT FOUND",
    257: "PATH NOT ALLOWED",
    258: "FILE TOO LARGE",
}


class BasicError(Exception):
    """Erreur Applesoft BASIC avec code et numéro de ligne optionnel."""

    def __init__(self, code: int, line_number: int | None = None):
        self.code = code
        self.line_number = line_number
        self.message = get_message(code)
        super().__init__(self.format())

    def format(self) -> str:
        """Formate le message d'erreur au format Applesoft."""
        return format_error(self.code, self.line_number)


class BasicSyntaxError(BasicError):
    """Erreur de syntaxe (code 16)."""

    def __init__(self, line_number: int | None = None):
        super().__init__(16, line_number)


def get_message(code: int) -> str:
    """Retourne le message d'erreur pour un code donné."""
    return ERROR_MESSAGES.get(code, "UNKNOWN")


def format_error(code: int, line_number: int | None = None) -> str:
    """Formate un message d'erreur au format Applesoft.

    Format : ?MESSAGE ERROR [IN linenum]
    Le numéro de ligne n'est affiché que pendant l'exécution d'un programme.
    """
    msg = f"?{get_message(code)} ERROR"
    if line_number is not None:
        msg += f" IN {line_number}"
    return msg


def raise_error(code: int, line_number: int | None = None) -> None:
    """Lève une erreur Applesoft."""
    raise BasicError(code, line_number)
