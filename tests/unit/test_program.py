"""Tests unitaires pour le module program (UC-001, UC-002)."""

from applesoft.lexer import TokenType, tokenize
from applesoft.program import Program


def _store_line(prog: Program, line: str) -> None:
    """Helper : tokenise une ligne numérotée et la stocke."""
    tokens = tokenize(line)
    if tokens and tokens[0].type == TokenType.LINENUM:
        num = tokens[0].value
        prog.add_line(num, tokens[1:])


class TestProgramStorage:
    """Tests pour le stockage des lignes."""

    def test_ca_uc_001_03_store_line(self):
        """CA-UC-001-03 : 10 PRINT "HELLO" → stocké sans exécution."""
        prog = Program()
        _store_line(prog, '10 PRINT "HELLO"')
        assert prog.has_line(10)

    def test_ca_uc_001_04_sorted_order(self):
        """CA-UC-001-04 : 20 puis 10 → ordre 10, 20."""
        prog = Program()
        _store_line(prog, '20 PRINT "B"')
        _store_line(prog, '10 PRINT "A"')
        assert prog.line_numbers() == [10, 20]

    def test_ca_uc_001_05_replace_line(self):
        """CA-UC-001-05 : 10 PRINT "Z" remplace la ligne 10 existante."""
        prog = Program()
        _store_line(prog, '10 PRINT "A"')
        _store_line(prog, '10 PRINT "Z"')
        line = prog.get_line(10)
        # Vérifier que le token STRING contient "Z"
        str_tokens = [t for t in line.tokens if t.type == TokenType.STRING]
        assert str_tokens[0].value == "Z"

    def test_ca_uc_001_06_delete_line(self):
        """CA-UC-001-06 : 10 seul → supprime la ligne 10."""
        prog = Program()
        _store_line(prog, '10 PRINT "A"')
        prog.delete_line(10)
        assert not prog.has_line(10)

    def test_delete_nonexistent(self):
        """Supprimer une ligne inexistante ne cause pas d'erreur."""
        prog = Program()
        prog.delete_line(99)  # Pas d'exception


class TestProgramList:
    """Tests pour LIST."""

    def test_ca_uc_002_01_list_all(self):
        """CA-UC-002-01 : LIST → affiche les lignes dans l'ordre."""
        prog = Program()
        _store_line(prog, '10 PRINT "A"')
        _store_line(prog, '20 PRINT "B"')
        _store_line(prog, '30 PRINT "C"')
        lines = prog.get_lines_range()
        assert len(lines) == 3
        assert lines[0].number == 10
        assert lines[1].number == 20
        assert lines[2].number == 30

    def test_ca_uc_002_02_list_single(self):
        """CA-UC-002-02 : LIST 20 → uniquement la ligne 20."""
        prog = Program()
        _store_line(prog, '10 PRINT "A"')
        _store_line(prog, '20 PRINT "B"')
        _store_line(prog, '30 PRINT "C"')
        lines = prog.get_lines_range(20, 20)
        assert len(lines) == 1
        assert lines[0].number == 20

    def test_ca_uc_002_03_list_range(self):
        """CA-UC-002-03 : LIST 10,20 → lignes 10 à 20."""
        prog = Program()
        _store_line(prog, '10 PRINT "A"')
        _store_line(prog, '20 PRINT "B"')
        _store_line(prog, '30 PRINT "C"')
        lines = prog.get_lines_range(10, 20)
        assert len(lines) == 2

    def test_ca_uc_002_04_new(self):
        """CA-UC-002-04 : NEW → LIST n'affiche rien."""
        prog = Program()
        _store_line(prog, '10 PRINT "A"')
        prog.clear()
        assert prog.is_empty()
        assert prog.get_lines_range() == []


class TestProgramDel:
    """Tests pour DEL."""

    def test_ca_uc_002_05_del_range(self):
        """CA-UC-002-05 : DEL 10,20 → supprime les lignes 10 à 20."""
        prog = Program()
        _store_line(prog, '10 PRINT "A"')
        _store_line(prog, '20 PRINT "B"')
        _store_line(prog, '30 PRINT "C"')
        prog.delete_range(10, 20)
        assert prog.line_numbers() == [30]

    def test_ca_uc_002_06_del_single_via_range(self):
        """CA-UC-002-06 : DEL 20,20 → supprime uniquement la ligne 20."""
        prog = Program()
        _store_line(prog, '10 PRINT "A"')
        _store_line(prog, '20 PRINT "B"')
        _store_line(prog, '30 PRINT "C"')
        prog.delete_range(20, 20)
        assert prog.line_numbers() == [10, 30]


class TestDetokenize:
    """Tests pour la détokenisation."""

    def test_detokenize_print_string(self):
        prog = Program()
        _store_line(prog, '10 PRINT "HELLO"')
        line = prog.get_line(10)
        text = prog.detokenize_line(line)
        assert "10" in text
        assert "PRINT" in text
        assert '"HELLO"' in text

    def test_detokenize_all(self):
        prog = Program()
        _store_line(prog, '10 PRINT "A"')
        _store_line(prog, '20 PRINT "B"')
        text = prog.detokenize_all()
        lines = text.split("\n")
        assert len(lines) == 2


class TestASTCache:
    """Tests pour le cache AST."""

    def test_cache_and_retrieve(self):
        prog = Program()
        _store_line(prog, '10 PRINT "HELLO"')
        prog.cache_ast(10, "fake_ast")
        assert prog.get_cached_ast(10) == "fake_ast"

    def test_replace_invalidates_cache(self):
        prog = Program()
        _store_line(prog, '10 PRINT "A"')
        prog.cache_ast(10, "old_ast")
        _store_line(prog, '10 PRINT "B"')
        assert prog.get_cached_ast(10) is None


class TestNavigation:
    """Tests pour la navigation dans le programme."""

    def test_next_line_number(self):
        prog = Program()
        _store_line(prog, '10 PRINT "A"')
        _store_line(prog, '20 PRINT "B"')
        _store_line(prog, '30 PRINT "C"')
        assert prog.next_line_number(10) == 20
        assert prog.next_line_number(20) == 30
        assert prog.next_line_number(30) is None

    def test_first_line_number(self):
        prog = Program()
        _store_line(prog, '20 PRINT "B"')
        _store_line(prog, '10 PRINT "A"')
        assert prog.first_line_number() == 10

    def test_first_line_empty(self):
        prog = Program()
        assert prog.first_line_number() is None
