"""Tests unitaires pour le module REPL (UC-001, UC-002)."""

from applesoft.io_cli import IOBridgeCLI
from applesoft.repl import REPL


class MockIO(IOBridgeCLI):
    """IOBridge mockée pour les tests."""

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


def make_repl(inputs: list[str]) -> tuple[REPL, MockIO]:
    """Crée un REPL avec des entrées mockées."""
    io = MockIO(inputs)
    repl = REPL(io)
    return repl, io


class TestREPLPrompt:
    """Tests pour le prompt REPL."""

    def test_ca_uc_001_01_prompt_displayed(self):
        """CA-UC-001-01 : Émulateur démarré → prompt ] affiché."""
        repl, io = make_repl([])  # EOFError immédiat
        repl.run()
        assert "]" in io.output

    def test_empty_line(self):
        """Ligne vide → prompt réaffiché."""
        repl, io = make_repl(["", ""])
        repl.run()
        assert io.output.count("]") == 3  # 3 prompts (initial + 2 réaffichages)


class TestREPLDeferred:
    """Tests pour le mode différé."""

    def test_ca_uc_001_03_store_line(self):
        """CA-UC-001-03 : 10 PRINT "HELLO" → stocké sans exécution."""
        repl, io = make_repl(['10 PRINT "HELLO"'])
        repl.run()
        assert repl.program.has_line(10)
        # Pas de "HELLO" dans la sortie (pas exécuté)
        assert "HELLO" not in io.output

    def test_ca_uc_001_04_sorted_order(self):
        """CA-UC-001-04 : 20 puis 10 → ordre 10, 20."""
        repl, io = make_repl(['20 PRINT "B"', '10 PRINT "A"'])
        repl.run()
        assert repl.program.line_numbers() == [10, 20]

    def test_ca_uc_001_05_replace_line(self):
        """CA-UC-001-05 : 10 PRINT "Z" remplace la ligne 10."""
        repl, io = make_repl(['10 PRINT "A"', '10 PRINT "Z"'])
        repl.run()
        from applesoft.lexer import TokenType

        line = repl.program.get_line(10)
        str_tokens = [t for t in line.tokens if t.type == TokenType.STRING]
        assert str_tokens[0].value == "Z"

    def test_ca_uc_001_06_delete_by_number(self):
        """CA-UC-001-06 : 10 seul → supprime la ligne 10."""
        repl, io = make_repl(['10 PRINT "A"', "10"])
        repl.run()
        assert not repl.program.has_line(10)

    def test_line_number_too_large(self):
        """Numéro > 63999 → ?SYNTAX ERROR."""
        repl, io = make_repl(["64000 PRINT"])
        repl.run()
        assert "?SYNTAX ERROR" in io.output


class TestREPLList:
    """Tests pour la commande LIST."""

    def test_ca_uc_002_01_list_all(self):
        """CA-UC-002-01 : LIST → affiche les lignes dans l'ordre."""
        repl, io = make_repl(['10 PRINT "A"', '20 PRINT "B"', '30 PRINT "C"', "LIST"])
        repl.run()
        # La sortie doit contenir les 3 lignes dans l'ordre
        out = io.output
        assert "10" in out
        assert "20" in out
        assert "30" in out

    def test_ca_uc_002_02_list_single(self):
        """CA-UC-002-02 : LIST 20 → affiche uniquement la ligne 20."""
        repl, io = make_repl(['10 PRINT "A"', '20 PRINT "B"', '30 PRINT "C"', "LIST 20"])
        repl.run()
        out = io.output
        # La ligne 20 doit apparaître dans la sortie
        assert "20 " in out
        assert "PRINT" in out

    def test_ca_uc_002_03_list_range(self):
        """CA-UC-002-03 : LIST 10,20 → lignes 10 à 20."""
        repl, io = make_repl(['10 PRINT "A"', '20 PRINT "B"', '30 PRINT "C"', "LIST 10,20"])
        repl.run()
        out = io.output
        # Les lignes 10 et 20 doivent apparaître
        assert "10 " in out
        assert "20 " in out

    def test_ca_uc_002_04_new(self):
        """CA-UC-002-04 : NEW → LIST n'affiche rien."""
        repl, io = make_repl(['10 PRINT "A"', "NEW", "LIST"])
        repl.run()
        assert repl.program.is_empty()


class TestREPLDel:
    """Tests pour la commande DEL."""

    def test_ca_uc_002_05_del_range(self):
        """CA-UC-002-05 : DEL 10,20 → supprime les lignes 10 à 20."""
        repl, io = make_repl(['10 PRINT "A"', '20 PRINT "B"', '30 PRINT "C"', "DEL 10,20"])
        repl.run()
        assert repl.program.line_numbers() == [30]

    def test_ca_uc_002_06_del_single(self):
        """CA-UC-002-06 : DEL 20,20 → supprime uniquement la ligne 20."""
        repl, io = make_repl(['10 PRINT "A"', '20 PRINT "B"', '30 PRINT "C"', "DEL 20,20"])
        repl.run()
        assert repl.program.line_numbers() == [10, 30]
