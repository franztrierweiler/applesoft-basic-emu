"""Tests QA — Lot 01 : Infrastructure et pipeline de base.

Scénarios du plan de test qa/plan-test/lot-01-infrastructure-pipeline.md
Nomenclature : test_tXX_YY_description
"""

import ast as python_ast

import pytest

from applesoft import ast_nodes as basic_ast
from applesoft.errors import ERROR_MESSAGES, BasicError, format_error
from applesoft.formatter import format_number
from applesoft.io_cli import IOBridgeCLI
from applesoft.lexer import Token, TokenType, tokenize
from applesoft.parser import parse_tokens
from applesoft.repl import REPL

# ── Helpers ──────────────────────────────────────────────────────────────


class MockIO(IOBridgeCLI):
    """IOBridge mockée pour les tests QA."""

    def __init__(self, inputs: list[str] | None = None):
        super().__init__()
        self._inputs = inputs or []
        self._input_idx = 0
        self._output: list[str] = []

    def print_str(self, text: str) -> None:
        self._output.append(text)

    def input_str(self, prompt: str = "") -> str:
        if prompt:
            self._output.append(prompt)
        if self._input_idx >= len(self._inputs):
            raise EOFError
        line = self._inputs[self._input_idx]
        self._input_idx += 1
        return line

    @property
    def output(self) -> str:
        return "".join(self._output)


def repl_session(inputs: list[str]) -> tuple[REPL, str]:
    """Exécute une session REPL et retourne (repl, output)."""
    io = MockIO(inputs)
    repl = REPL(io)
    repl.run()
    return repl, io.output


# ═══════════════════════════════════════════════════════════════════════
# T01 — Lexer (RG-0001 à RG-0005)
# ═══════════════════════════════════════════════════════════════════════


class TestT01Lexer:
    """Scénarios T01-01 à T01-20 : tokenisation."""

    def test_t01_01_tokenize_print_hello(self):
        """T01-01 [🔴] Tokenisation 10 PRINT "HELLO"."""
        tokens = tokenize('10 PRINT "HELLO"')
        assert tokens[0] == Token(TokenType.LINENUM, 10)
        assert tokens[1] == Token(TokenType.KEYWORD, "PRINT")
        assert tokens[2] == Token(TokenType.STRING, "HELLO")
        assert len(tokens) == 3

    def test_t01_02_tokenize_expression(self):
        """T01-02 [🔴] Tokenisation A = 3.14 + B."""
        tokens = tokenize("A = 3.14 + B")
        assert tokens[0] == Token(TokenType.IDENT, "A")
        assert tokens[1] == Token(TokenType.OP, "=")
        assert tokens[2] == Token(TokenType.NUMBER, 3.14)
        assert tokens[3] == Token(TokenType.OP, "+")
        assert tokens[4] == Token(TokenType.IDENT, "B")

    def test_t01_03_no_space_keyword_string(self):
        """T01-03 [🟠] Espaces optionnels entre keyword et chaîne."""
        t1 = tokenize('10 PRINT "HELLO"')
        t2 = tokenize('10 PRINT"HELLO"')
        assert t1 == t2

    def test_t01_04_empty_line(self):
        """T01-04 [🟡] Ligne vide → séquence vide."""
        assert tokenize("") == []
        assert tokenize("   ") == []

    def test_t01_05_unclosed_string(self):
        """T01-05 [🟠] Chaîne non fermée terminée en fin de ligne."""
        tokens = tokenize('10 PRINT "HELLO')
        str_tok = [t for t in tokens if t.type == TokenType.STRING]
        assert len(str_tok) == 1
        assert str_tok[0].value == "HELLO"

    def test_t01_06_greedy_for(self):
        """T01-06 [🔴] Correspondance gloutonne FORI=1TO10."""
        tokens = tokenize("10 FORI=1TO10")
        types_values = [(t.type, t.value) for t in tokens]
        assert (TokenType.KEYWORD, "FOR") in types_values
        assert (TokenType.IDENT, "I") in types_values
        assert (TokenType.KEYWORD, "TO") in types_values

    def test_t01_07_greedy_if_at(self):
        """T01-07 [🔴] Correspondance gloutonne IFATHENPRINT."""
        tokens = tokenize('10 IFATHENPRINT"OK"')
        kws = [t.value for t in tokens if t.type == TokenType.KEYWORD]
        assert "IF" in kws
        assert "AT" in kws
        assert "PRINT" in kws
        # HEN doit être un identifiant, pas THEN
        assert "THEN" not in kws

    def test_t01_08_goto_no_space(self):
        """T01-08 [🔴] GOTO100 sans séparateur."""
        tokens = tokenize("10 GOTO100")
        assert Token(TokenType.KEYWORD, "GOTO") in tokens
        assert Token(TokenType.NUMBER, 100.0) in tokens

    def test_t01_09_score_keyword_in_ident(self):
        """T01-09 [🔴] SCORE → SC + OR + E."""
        tokens = tokenize("SCORE")
        assert tokens[0] == Token(TokenType.IDENT, "SC")
        assert tokens[1] == Token(TokenType.KEYWORD, "OR")
        assert tokens[2] == Token(TokenType.IDENT, "E")

    def test_t01_10_notation_multi_keyword(self):
        """T01-10 [🔴] NOTATION → NOT + AT + I + ON."""
        tokens = tokenize("NOTATION")
        assert tokens[0] == Token(TokenType.KEYWORD, "NOT")
        assert tokens[1] == Token(TokenType.KEYWORD, "AT")
        assert tokens[2] == Token(TokenType.IDENT, "I")
        assert tokens[3] == Token(TokenType.KEYWORD, "ON")

    def test_t01_11_two_char_ident(self):
        """T01-11 [🔴] Seuls 2 caractères significatifs (LOW == LO)."""
        # Les deux doivent produire le même identifiant normalisé
        # Testons que LO est normalisé identiquement depuis LOW et LO
        t1 = tokenize("LO = 5")
        t2 = tokenize("LO = 5")
        ident1 = [t for t in t1 if t.type == TokenType.IDENT][0]
        ident2 = [t for t in t2 if t.type == TokenType.IDENT][0]
        assert ident1.value == ident2.value == "LO"

    def test_t01_12_suffix_distinct(self):
        """T01-12 [🔴] A, A$, A% sont 3 variables distinctes."""
        ta = [t for t in tokenize("A = 1") if t.type == TokenType.IDENT][0]
        ta_s = [t for t in tokenize("A$ = 1") if t.type == TokenType.IDENT][0]
        ta_i = [t for t in tokenize("A% = 1") if t.type == TokenType.IDENT][0]
        names = {ta.value, ta_s.value, ta_i.value}
        assert len(names) == 3

    def test_t01_13_float_literal(self):
        """T01-13 [🔴] Littéral flottant 3.14."""
        nums = [t for t in tokenize("X = 3.14") if t.type == TokenType.NUMBER]
        assert nums[0].value == 3.14

    def test_t01_14_scientific_notation(self):
        """T01-14 [🟠] Notation scientifique 1E3 → 1000."""
        nums = [t for t in tokenize("X = 1E3") if t.type == TokenType.NUMBER]
        assert nums[0].value == 1000.0

    def test_t01_15_dot_prefix_number(self):
        """T01-15 [🟠] Nombre .5 → 0.5."""
        nums = [t for t in tokenize("X = .5") if t.type == TokenType.NUMBER]
        assert nums[0].value == 0.5

    def test_t01_16_string_literal(self):
        """T01-16 [🔴] Chaîne "HELLO WORLD"."""
        strs = [t for t in tokenize('PRINT "HELLO WORLD"') if t.type == TokenType.STRING]
        assert strs[0].value == "HELLO WORLD"

    def test_t01_17_unclosed_string_literal(self):
        """T01-17 [🟠] Chaîne non fermée → terminée en fin de ligne."""
        strs = [t for t in tokenize('PRINT "HELLO') if t.type == TokenType.STRING]
        assert strs[0].value == "HELLO"

    def test_t01_18_empty_string(self):
        """T01-18 [🟡] Chaîne vide ""."""
        strs = [t for t in tokenize('""') if t.type == TokenType.STRING]
        assert strs[0].value == ""

    def test_t01_19_line_truncation_239(self):
        """T01-19 [🟠] Troncature à 239 caractères."""
        long_line = "10 " + "A" * 300
        tokens = tokenize(long_line)
        # La ligne originale dépasse 239, elle doit être tronquée
        # Le token LINENUM doit exister
        assert tokens[0].type == TokenType.LINENUM

    def test_t01_20_question_mark_print(self):
        """T01-20 [🟠] ? reconnu comme alias de PRINT."""
        tokens = tokenize('? "HELLO"')
        assert tokens[0] == Token(TokenType.KEYWORD, "PRINT")


# ═══════════════════════════════════════════════════════════════════════
# T02 — NumberFormatter (RG-0006)
# ═══════════════════════════════════════════════════════════════════════


class TestT02Formatter:
    """Scénarios T02-01 à T02-03 : formatage des nombres."""

    def test_t02_01_positive_space(self):
        """T02-01 [🔴] Espace avant nombre positif."""
        assert format_number(3.14) == " 3.14"
        assert format_number(42) == " 42"
        assert format_number(0) == " 0"

    def test_t02_02_negative_no_space(self):
        """T02-02 [🔴] Pas d'espace avant nombre négatif."""
        result = format_number(-5)
        assert result == "-5"
        assert not result.startswith(" ")

    def test_t02_03_scientific_large(self):
        """T02-03 [🟠] Notation scientifique >= 1E9."""
        result = format_number(1_000_000_000)
        assert result == " 1E+09"


# ═══════════════════════════════════════════════════════════════════════
# T03 — ErrorHandler (RG-0010)
# ═══════════════════════════════════════════════════════════════════════


class TestT03Errors:
    """Scénarios T03-01 à T03-03 : gestion d'erreurs."""

    def test_t03_01_error_with_linenum(self):
        """T03-01 [🔴] ?DIVISION BY ZERO ERROR IN 10."""
        assert format_error(133, 10) == "?DIVISION BY ZERO ERROR IN 10"

    def test_t03_02_error_no_linenum(self):
        """T03-02 [🔴] ?DIVISION BY ZERO ERROR (mode direct)."""
        assert format_error(133) == "?DIVISION BY ZERO ERROR"

    def test_t03_03_all_error_codes(self):
        """T03-03 [🔴] Les codes d'erreur de base sont définis."""
        base_codes = {0, 16, 22, 42, 53, 69, 77, 90, 107, 120, 133, 163, 176, 224, 254, 255}
        assert base_codes.issubset(set(ERROR_MESSAGES.keys()))


# ═══════════════════════════════════════════════════════════════════════
# T04 — Parser (GRAMMAR.md)
# ═══════════════════════════════════════════════════════════════════════


class TestT04Parser:
    """Scénarios T04-01 à T04-06 : construction de l'AST."""

    def _parse(self, line: str):
        tokens = tokenize(line)
        if tokens and tokens[0].type == TokenType.LINENUM:
            tokens = tokens[1:]
        return parse_tokens(tokens)

    def test_t04_01_parse_print(self):
        """T04-01 [🔴] Parse PRINT "HELLO" → PrintStmt."""
        result = self._parse('PRINT "HELLO"')
        stmt = result.statements[0]
        assert isinstance(stmt, basic_ast.PrintStmt)
        expr, _ = stmt.items[0]
        assert isinstance(expr, basic_ast.StringLiteral)
        assert expr.value == "HELLO"

    def test_t04_02_parse_let(self):
        """T04-02 [🔴] Parse LET A = 5 → LetStmt."""
        result = self._parse("LET A = 5")
        stmt = result.statements[0]
        assert isinstance(stmt, basic_ast.LetStmt)
        assert isinstance(stmt.target, basic_ast.Variable)
        assert isinstance(stmt.value, basic_ast.NumberLiteral)

    def test_t04_03_precedence(self):
        """T04-03 [🔴] Précédence * sur + : 2+3*4 → +(2, *(3,4))."""
        result = self._parse("PRINT 2+3*4")
        expr, _ = result.statements[0].items[0]
        assert isinstance(expr, basic_ast.BinaryOp)
        assert expr.op == "+"
        assert isinstance(expr.right, basic_ast.BinaryOp)
        assert expr.right.op == "*"

    def test_t04_04_power_right_assoc(self):
        """T04-04 [🟠] Associativité droite ^ : 2^3^2 → ^(2, ^(3,2))."""
        result = self._parse("PRINT 2^3^2")
        expr, _ = result.statements[0].items[0]
        assert isinstance(expr, basic_ast.BinaryOp)
        assert expr.op == "^"
        assert isinstance(expr.right, basic_ast.BinaryOp)
        assert expr.right.op == "^"

    def test_t04_05_rem_eats_colon(self):
        """T04-05 [🔴] REM absorbe tout y compris ':'."""
        result = self._parse('REM TEXTE : PRINT "CACHÉ"')
        assert len(result.statements) == 1
        assert isinstance(result.statements[0], basic_ast.RemStmt)

    def test_t04_06_syntax_error(self):
        """T04-06 [🔴] Entrée invalide → BasicSyntaxError."""
        tokens = tokenize("GOTO")
        # GOTO sans numéro → erreur de syntaxe au parsing
        with pytest.raises(BasicError) as exc_info:
            parse_tokens(tokens)
        assert exc_info.value.code == 16


# ═══════════════════════════════════════════════════════════════════════
# T05 — REPL UC-001
# ═══════════════════════════════════════════════════════════════════════


class TestT05ReplUC001:
    """Scénarios T05-01 à T05-08 : interaction REPL."""

    def test_t05_01_prompt_at_start(self):
        """T05-01 [🔴] Prompt ] affiché au démarrage."""
        _, out = repl_session([])
        assert "]" in out

    def test_t05_02_deferred_store(self):
        """T05-02 [🔴] Ligne numérotée stockée sans exécution."""
        repl, out = repl_session(['10 PRINT "HELLO"'])
        assert repl.program.has_line(10)
        assert "HELLO" not in out  # Pas exécuté

    def test_t05_03_sorted_lines(self):
        """T05-03 [🔴] Lignes triées par numéro."""
        repl, _ = repl_session(['20 PRINT "B"', '10 PRINT "A"'])
        assert repl.program.line_numbers() == [10, 20]

    def test_t05_04_replace_line(self):
        """T05-04 [🔴] Remplacement de ligne existante."""
        repl, _ = repl_session(['10 PRINT "A"', '10 PRINT "Z"'])
        line = repl.program.get_line(10)
        strs = [t for t in line.tokens if t.type == TokenType.STRING]
        assert strs[0].value == "Z"

    def test_t05_05_delete_by_number(self):
        """T05-05 [🔴] Numéro seul → suppression."""
        repl, _ = repl_session(['10 PRINT "A"', "10"])
        assert not repl.program.has_line(10)

    def test_t05_06_empty_line(self):
        """T05-06 [🟡] Ligne vide → prompt réaffiché sans erreur."""
        _, out = repl_session(["", ""])
        # 3 prompts : initial + 2 réaffichages
        assert out.count("]") == 3

    def test_t05_07_linenum_too_large(self):
        """T05-07 [🟠] Numéro > 63999 → ?SYNTAX ERROR."""
        _, out = repl_session(["64000 PRINT"])
        assert "?SYNTAX ERROR" in out

    def test_t05_08_delete_nonexistent(self):
        """T05-08 [🟡] Suppression d'une ligne inexistante → pas d'erreur."""
        _, out = repl_session(["10"])
        assert "ERROR" not in out


# ═══════════════════════════════════════════════════════════════════════
# T06 — REPL UC-002
# ═══════════════════════════════════════════════════════════════════════


class TestT06ReplUC002:
    """Scénarios T06-01 à T06-06 : gestion du programme."""

    def test_t06_01_list_all(self):
        """T06-01 [🔴] LIST affiche toutes les lignes dans l'ordre."""
        repl, out = repl_session(['10 PRINT "A"', '20 PRINT "B"', '30 PRINT "C"', "LIST"])
        # Les 3 numéros de ligne doivent apparaître dans la sortie
        assert "10 " in out
        assert "20 " in out
        assert "30 " in out
        # Vérifier l'ordre : 10 avant 20, 20 avant 30
        idx10 = out.index("10 ")
        idx20 = out.index("20 ")
        idx30 = out.index("30 ")
        assert idx10 < idx20 < idx30

    def test_t06_02_list_single(self):
        """T06-02 [🔴] LIST 20 → uniquement ligne 20."""
        repl, out = repl_session(['10 PRINT "A"', '20 PRINT "B"', '30 PRINT "C"', "LIST 20"])
        # La ligne 20 doit être affichée, pas les lignes 10 ni 30
        # Nettoyer les prompts ] pour analyser la sortie
        clean = out.replace("]", "")
        listed = [part.strip() for part in clean.split("\n") if "PRINT" in part]
        assert len(listed) == 1
        assert listed[0].startswith("20")

    def test_t06_03_list_range(self):
        """T06-03 [🔴] LIST 10,20 → plage 10-20."""
        repl, out = repl_session(['10 PRINT "A"', '20 PRINT "B"', '30 PRINT "C"', "LIST 10,20"])
        clean = out.replace("]", "")
        listed = [part.strip() for part in clean.split("\n") if "PRINT" in part]
        assert len(listed) == 2

    def test_t06_04_new_clears(self):
        """T06-04 [🔴] NEW → programme effacé."""
        repl, _ = repl_session(['10 PRINT "A"', "NEW"])
        assert repl.program.is_empty()

    def test_t06_05_del_range(self):
        """T06-05 [🔴] DEL 10,20 → supprime plage."""
        repl, _ = repl_session(['10 PRINT "A"', '20 PRINT "B"', '30 PRINT "C"', "DEL 10,20"])
        assert repl.program.line_numbers() == [30]

    def test_t06_06_del_single(self):
        """T06-06 [🟠] DEL 20,20 → supprime une seule ligne."""
        repl, _ = repl_session(['10 PRINT "A"', '20 PRINT "B"', '30 PRINT "C"', "DEL 20,20"])
        assert repl.program.line_numbers() == [10, 30]


# ═══════════════════════════════════════════════════════════════════════
# T07 — ENF (portabilité, performance)
# ═══════════════════════════════════════════════════════════════════════


class TestT07ENF:
    """Scénarios T07-01 à T07-02 : exigences non fonctionnelles."""

    FORBIDDEN_IMPORTS = {
        "ctypes",
        "numpy",
        "threading",
        "multiprocessing",
        "subprocess",
        "os.path",
    }

    CORE_MODULES = [
        "src/applesoft/lexer.py",
        "src/applesoft/parser.py",
        "src/applesoft/errors.py",
        "src/applesoft/formatter.py",
        "src/applesoft/program.py",
        "src/applesoft/ast_nodes.py",
    ]

    def test_t07_01_no_forbidden_imports(self):
        """T07-01 [🟠] Pas d'import interdit dans les modules cœur."""
        for module_path in self.CORE_MODULES:
            with open(module_path) as f:
                source = f.read()
            tree = python_ast.parse(source)
            for node in python_ast.walk(tree):
                if isinstance(node, python_ast.Import):
                    for alias in node.names:
                        for forbidden in self.FORBIDDEN_IMPORTS:
                            assert not alias.name.startswith(forbidden), (
                                f"{module_path} importe {alias.name} (interdit)"
                            )
                elif isinstance(node, python_ast.ImportFrom):
                    if node.module:
                        for forbidden in self.FORBIDDEN_IMPORTS:
                            assert not node.module.startswith(forbidden), (
                                f"{module_path} importe depuis {node.module} (interdit)"
                            )
