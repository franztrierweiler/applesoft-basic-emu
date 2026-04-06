"""Tests unitaires pour le module environment."""

import pytest

from applesoft.environment import Environment
from applesoft.errors import BasicError


class TestVariables:
    """Tests pour les variables."""

    def test_default_numeric(self):
        env = Environment()
        assert env.get_var("X") == 0

    def test_default_string(self):
        env = Environment()
        assert env.get_var("A$") == ""

    def test_set_get(self):
        env = Environment()
        env.set_var("X", 42.0)
        assert env.get_var("X") == 42.0

    def test_set_string(self):
        env = Environment()
        env.set_var("A$", "HELLO")
        assert env.get_var("A$") == "HELLO"

    def test_type_mismatch_string_to_numeric(self):
        """CA-RG-0007-04 : A="TEXT" → TYPE MISMATCH."""
        env = Environment()
        with pytest.raises(BasicError) as exc_info:
            env.set_var("A", "TEXT")
        assert exc_info.value.code == 163

    def test_type_mismatch_numeric_to_string(self):
        """CA-RG-0007-03 : A$=5 → TYPE MISMATCH."""
        env = Environment()
        with pytest.raises(BasicError) as exc_info:
            env.set_var("A$", 5)
        assert exc_info.value.code == 163

    def test_integer_truncation(self):
        """CA-RG-0006-05 : X%=3.7 → tronqué à 3."""
        env = Environment()
        env.set_var("X%", 3.7)
        assert env.get_var("X%") == 3

    def test_integer_overflow(self):
        """CA-RG-0006-04 : X%=32768 → ILLEGAL QUANTITY."""
        env = Environment()
        with pytest.raises(BasicError) as exc_info:
            env.set_var("X%", 32768)
        assert exc_info.value.code == 53


class TestArrays:
    """Tests pour les tableaux."""

    def test_dim_and_access(self):
        """CA-UC-010-04 : DIM A(5) / A(3)=42 / A(3) → 42."""
        env = Environment()
        env.dim_array("A", [5])
        env.set_array("A", [3], 42.0)
        assert env.get_array("A", [3]) == 42.0

    def test_dim_2d(self):
        """CA-UC-010-05 : DIM B(2,3) / B(1,2)=7 / B(1,2) → 7."""
        env = Environment()
        env.dim_array("B", [2, 3])
        env.set_array("B", [1, 2], 7.0)
        assert env.get_array("B", [1, 2]) == 7.0

    def test_auto_dim(self):
        """CA-UC-010-06 : A(3)=5 sans DIM → auto-dim à 10."""
        env = Environment()
        env.set_array("A", [3], 5.0)
        assert env.get_array("A", [3]) == 5.0

    def test_redim_error(self):
        env = Environment()
        env.dim_array("A", [5])
        with pytest.raises(BasicError) as exc_info:
            env.dim_array("A", [10])
        assert exc_info.value.code == 120

    def test_bad_subscript(self):
        env = Environment()
        env.dim_array("A", [5])
        with pytest.raises(BasicError) as exc_info:
            env.get_array("A", [6])
        assert exc_info.value.code == 107


class TestReset:
    """Tests pour le reset."""

    def test_reset_clears_variables(self):
        env = Environment()
        env.set_var("X", 42.0)
        env.reset()
        assert env.get_var("X") == 0
