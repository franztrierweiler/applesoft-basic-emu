"""Tests unitaires pour le module errors (RG-0010)."""

from applesoft.errors import (
    BasicError,
    BasicSyntaxError,
    format_error,
    get_message,
)


class TestErrorMessages:
    """Tests pour la table des messages d'erreur."""

    def test_get_message_division_by_zero(self):
        assert get_message(133) == "DIVISION BY ZERO"

    def test_get_message_syntax(self):
        assert get_message(16) == "SYNTAX"

    def test_get_message_type_mismatch(self):
        assert get_message(163) == "TYPE MISMATCH"

    def test_get_message_unknown_code(self):
        assert get_message(999) == "UNKNOWN"

    def test_all_17_error_codes(self):
        """Vérifie que les 17 codes d'erreur sont définis."""
        from applesoft.errors import ERROR_MESSAGES

        expected_codes = {0, 16, 22, 42, 53, 69, 77, 90, 107, 120, 133, 163, 176, 224, 254, 255}
        assert expected_codes.issubset(set(ERROR_MESSAGES.keys()))


class TestFormatError:
    """Tests pour le formatage des messages d'erreur."""

    def test_ca_rg_0010_01_error_with_line_number(self):
        """CA-RG-0010-01 : ?DIVISION BY ZERO ERROR IN 10"""
        assert format_error(133, 10) == "?DIVISION BY ZERO ERROR IN 10"

    def test_ca_rg_0010_02_error_without_line_number(self):
        """CA-RG-0010-02 : ?DIVISION BY ZERO ERROR (sans numéro)"""
        assert format_error(133) == "?DIVISION BY ZERO ERROR"

    def test_syntax_error_format(self):
        assert format_error(16) == "?SYNTAX ERROR"

    def test_syntax_error_with_line(self):
        assert format_error(16, 100) == "?SYNTAX ERROR IN 100"


class TestBasicError:
    """Tests pour l'exception BasicError."""

    def test_basic_error_attributes(self):
        err = BasicError(133, 10)
        assert err.code == 133
        assert err.line_number == 10
        assert err.message == "DIVISION BY ZERO"

    def test_basic_error_format(self):
        err = BasicError(133, 10)
        assert err.format() == "?DIVISION BY ZERO ERROR IN 10"

    def test_basic_syntax_error(self):
        err = BasicSyntaxError(20)
        assert err.code == 16
        assert err.format() == "?SYNTAX ERROR IN 20"
