"""Tests unitaires pour MemoryMap (UC-022, RG-0011).

Couvre PEEK/POKE/CALL, soft-switches, et validation des bornes.
"""

import pytest

from applesoft.memory import MemoryMap


class FakeEnvironment:
    """Environnement minimal pour les tests MemoryMap."""

    def __init__(self):
        self._error_code = 0
        self._error_line = 0

    def get_error_code(self) -> int:
        return self._error_code

    def set_error_code(self, code: int) -> None:
        self._error_code = code

    def get_error_line(self) -> int:
        return self._error_line

    def set_error_line(self, line: int) -> None:
        self._error_line = line


class FakeIO:
    """IOBridge minimal pour les tests MemoryMap."""

    def __init__(self):
        self.cleared = False
        self._last_key = 0
        self._cursor_column = 1

    def clear_screen(self) -> None:
        self.cleared = True

    def get_last_key(self) -> int:
        return self._last_key

    def set_last_key(self, key: int) -> None:
        self._last_key = key

    def get_cursor_column(self) -> int:
        return self._cursor_column

    def print_str(self, text: str) -> None:
        pass


# --- Tests PEEK/POKE basiques ---


class TestPeekPoke:
    """Tests lecture/écriture mémoire."""

    def setup_method(self):
        self.env = FakeEnvironment()
        self.io = FakeIO()
        self.mem = MemoryMap(self.env, self.io)

    def test_ca_uc_022_02_poke_peek_roundtrip(self):
        """CA-UC-022-02 : POKE 768,42 : PRINT PEEK(768) → 42."""
        self.mem.poke(768, 42)
        assert self.mem.peek(768) == 42

    def test_peek_default_zero(self):
        """Mémoire initialisée à 0."""
        assert self.mem.peek(768) == 0

    def test_poke_peek_boundary_0(self):
        """Adresse 0 valide."""
        self.mem.poke(0, 255)
        assert self.mem.peek(0) == 255

    def test_poke_peek_boundary_65535(self):
        """Adresse 65535 valide."""
        self.mem.poke(65535, 128)
        assert self.mem.peek(65535) == 128

    def test_peek_address_negative_error(self):
        """PEEK(-1) → ILLEGAL QUANTITY ERROR."""
        from applesoft.errors import BasicError

        with pytest.raises(BasicError) as exc_info:
            self.mem.peek(-1)
        assert exc_info.value.code == 53

    def test_peek_address_too_large_error(self):
        """PEEK(65536) → ILLEGAL QUANTITY ERROR."""
        from applesoft.errors import BasicError

        with pytest.raises(BasicError) as exc_info:
            self.mem.peek(65536)
        assert exc_info.value.code == 53

    def test_poke_address_too_large_error(self):
        """POKE 65536,0 → ILLEGAL QUANTITY ERROR."""
        from applesoft.errors import BasicError

        with pytest.raises(BasicError) as exc_info:
            self.mem.poke(65536, 0)
        assert exc_info.value.code == 53

    def test_poke_value_too_large_error(self):
        """POKE 768,256 → ILLEGAL QUANTITY ERROR."""
        from applesoft.errors import BasicError

        with pytest.raises(BasicError) as exc_info:
            self.mem.poke(768, 256)
        assert exc_info.value.code == 53

    def test_poke_value_negative_error(self):
        """POKE 768,-1 → ILLEGAL QUANTITY ERROR."""
        from applesoft.errors import BasicError

        with pytest.raises(BasicError) as exc_info:
            self.mem.poke(768, -1)
        assert exc_info.value.code == 53


# --- Tests soft-switches (RG-0011) ---


class TestSoftSwitches:
    """Tests des adresses mémoire émulées."""

    def setup_method(self):
        self.env = FakeEnvironment()
        self.io = FakeIO()
        self.mem = MemoryMap(self.env, self.io)

    def test_peek_222_error_code(self):
        """PEEK(222) → code dernière erreur."""
        self.env.set_error_code(133)
        assert self.mem.peek(222) == 133

    def test_peek_218_219_error_line(self):
        """PEEK(218-219) → numéro de ligne dernière erreur (little-endian)."""
        self.env.set_error_line(300)
        # 300 = 0x012C → low byte = 0x2C (44), high byte = 0x01 (1)
        assert self.mem.peek(218) == 44  # low byte
        assert self.mem.peek(219) == 1  # high byte

    def test_ca_uc_022_04_peek_49152_keyboard(self):
        """CA-UC-022-04 : PEEK(49152) → dernière touche avec bit 7."""
        self.io.set_last_key(ord("A") + 128)  # 193
        assert self.mem.peek(49152) == 193

    def test_ca_uc_022_05_poke_49168_reset_strobe(self):
        """CA-UC-022-05 : POKE 49168,0 → reset strobe clavier."""
        self.io.set_last_key(193)  # 'A' + 128
        self.mem.poke(49168, 0)
        # Après reset, le bit 7 doit être à 0
        assert self.io.get_last_key() < 128

    def test_peek_49200_speaker_noop(self):
        """POKE 49200,0 → speaker (no-op, pas d'erreur)."""
        self.mem.poke(49200, 0)  # Ne doit pas lever d'erreur

    def test_peek_48_text_mode(self):
        """PEEK(48) → mode texte/graphique."""
        # Par défaut, mode texte = 0
        assert self.mem.peek(48) == 0

    def test_peek_103_104_program_start(self):
        """PEEK(103-104) → adresse début programme (émulée)."""
        # Adresse émulée : 0x0801 (2049)
        assert self.mem.peek(103) == 1  # low byte
        assert self.mem.peek(104) == 8  # high byte


# --- Tests CALL ---


class TestCall:
    """Tests des routines émulées."""

    def setup_method(self):
        self.env = FakeEnvironment()
        self.io = FakeIO()
        self.mem = MemoryMap(self.env, self.io)

    def test_ca_uc_022_03_call_minus_936_home(self):
        """CA-UC-022-03 : CALL -936 → HOME (clear screen)."""
        self.mem.call(-936)
        assert self.io.cleared

    def test_call_minus_958_clreol(self):
        """CALL -958 → CLREOL (no-op pour l'instant, pas d'erreur)."""
        self.mem.call(-958)  # Ne doit pas lever d'erreur

    def test_call_minus_868_clreop(self):
        """CALL -868 → CLREOP (no-op pour l'instant, pas d'erreur)."""
        self.mem.call(-868)  # Ne doit pas lever d'erreur

    def test_call_62450_setinv(self):
        """CALL 62450 → SETINV (INVERSE)."""
        self.mem.call(62450)  # Ne doit pas lever d'erreur

    def test_call_62454_setnorm(self):
        """CALL 62454 → SETNORM (NORMAL)."""
        self.mem.call(62454)  # Ne doit pas lever d'erreur

    def test_call_address_out_of_range(self):
        """CALL 65536 → ILLEGAL QUANTITY ERROR."""
        from applesoft.errors import BasicError

        with pytest.raises(BasicError) as exc_info:
            self.mem.call(65536)
        assert exc_info.value.code == 53

    def test_call_unknown_address_no_error(self):
        """CALL adresse non émulée → pas d'erreur (avertissement optionnel)."""
        # Ne doit pas lever d'erreur
        self.mem.call(12345)
