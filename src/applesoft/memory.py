"""Carte mémoire émulée 64 Ko (UC-022, RG-0011, SEC-SPE-02).

Bytearray 64 Ko avec handlers de soft-switches pour les adresses
documentées. PEEK/POKE/CALL accèdent uniquement à cette mémoire
émulée, jamais à la mémoire Python réelle.
"""

from __future__ import annotations

import sys

from .errors import BasicError


class MemoryMap:
    """Carte mémoire 64 Ko avec soft-switches."""

    # Adresse début programme émulée : 0x0801 (2049)
    _PROGRAM_START = 0x0801

    def __init__(self, env, io):
        self._memory = bytearray(65536)
        self._env = env
        self._io = io
        # Mode texte/graphique (0 = texte)
        self._text_mode = 0
        # État INVERSE/NORMAL
        self._inverse = False

    def peek(self, address: int) -> int:
        """Lit un octet à l'adresse donnée (0-65535)."""
        address = int(address)
        if address < 0 or address > 65535:
            raise BasicError(53)  # ILLEGAL QUANTITY

        # Soft-switches (RG-0011)
        if address == 222:
            return self._env.get_error_code() & 0xFF
        if address == 218:
            return self._env.get_error_line() & 0xFF  # low byte
        if address == 219:
            return (self._env.get_error_line() >> 8) & 0xFF  # high byte
        if address == 49152:  # $C000 — KBD
            return self._io.get_last_key()
        if address == 48:  # $30 — TXTMODE
            return self._text_mode
        if address == 103:  # TXTTAB low byte
            return self._PROGRAM_START & 0xFF
        if address == 104:  # TXTTAB high byte
            return (self._PROGRAM_START >> 8) & 0xFF

        return self._memory[address]

    def poke(self, address: int, value: int) -> None:
        """Écrit un octet à l'adresse donnée."""
        address = int(address)
        value = int(value)
        if address < 0 or address > 65535:
            raise BasicError(53)  # ILLEGAL QUANTITY
        if value < 0 or value > 255:
            raise BasicError(53)  # ILLEGAL QUANTITY

        # Soft-switches (RG-0011)
        if address == 49168:  # $C010 — KBDSTRB (reset strobe clavier)
            last_key = self._io.get_last_key()
            self._io.set_last_key(last_key & 0x7F)  # Clear bit 7
            return
        if address == 49200:  # $C030 — SPKR (speaker, no-op)
            return

        self._memory[address] = value

    def call(self, address: int) -> None:
        """Exécute une routine émulée à l'adresse donnée."""
        address = int(address)
        if address < -32768 or address > 65535:
            raise BasicError(53)  # ILLEGAL QUANTITY

        # Normaliser les adresses négatives (complément à 2 sur 16 bits)
        if address < 0:
            address = address + 65536

        # Routines émulées
        if address == 64600:  # -936 + 65536 = 64600 → HOME
            self._io.clear_screen()
            return
        if address == 64578:  # -958 + 65536 = 64578 → CLREOL
            # No-op pour l'instant (effacer fin de ligne)
            return
        if address == 64668:  # -868 + 65536 = 64668 → CLREOP
            # No-op pour l'instant (effacer fin d'écran)
            return
        if address == 62450:  # SETINV (INVERSE)
            self._inverse = True
            return
        if address == 62454:  # SETNORM (NORMAL)
            self._inverse = False
            return

        # Adresse non émulée : avertissement sur stderr (SEC-SPE-02)
        print(
            f"WARNING: CALL {address} — adresse non émulée",
            file=sys.stderr,
        )
