"""Tests unitaires pour le module formatter (RG-0006)."""

from applesoft.formatter import format_number


class TestFormatNumber:
    """Tests pour le formatage des nombres Applesoft."""

    def test_ca_rg_0006_01_positive_float(self):
        """CA-RG-0006-01 : PRINT 3.14 → ' 3.14'"""
        result = format_number(3.14)
        assert result == " 3.14"

    def test_ca_rg_0006_02_negative_integer(self):
        """CA-RG-0006-02 : PRINT -5 → '-5'"""
        result = format_number(-5)
        assert result == "-5"

    def test_ca_rg_0006_03_scientific_notation(self):
        """CA-RG-0006-03 : PRINT 1000000000 → ' 1E+09'"""
        result = format_number(1000000000)
        assert result == " 1E+09"

    def test_zero(self):
        assert format_number(0) == " 0"

    def test_positive_integer(self):
        result = format_number(42)
        assert result == " 42"

    def test_negative_float(self):
        result = format_number(-3.14)
        assert result.startswith("-")
        assert "3.14" in result

    def test_small_positive(self):
        """Les très petits nombres positifs utilisent la notation scientifique."""
        result = format_number(0.001)
        assert result.startswith(" ")
        assert "E" in result

    def test_one(self):
        assert format_number(1) == " 1"

    def test_large_number_scientific(self):
        """Les nombres >= 1E9 sont en notation scientifique."""
        result = format_number(5e10)
        assert "E" in result
        assert result.startswith(" ")
