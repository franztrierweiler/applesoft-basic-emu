"""Interface abstraite d'I/O (protocole Python).

Toute interaction avec l'extérieur transite par cette interface.
Deux implémentations : IOBridgeCLI (terminal) et IOBridgeWeb (DOM/canvas).
"""

from __future__ import annotations

from typing import Protocol


class IOBridge(Protocol):
    """Interface abstraite d'entrées/sorties."""

    def print_str(self, text: str) -> None:
        """Affiche une chaîne de caractères."""
        ...

    def input_str(self, prompt: str = "") -> str:
        """Lit une ligne de texte avec un prompt optionnel."""
        ...

    def get_char(self) -> str:
        """Lit un caractère sans écho."""
        ...

    def clear_screen(self) -> None:
        """Efface l'écran."""
        ...

    def check_interrupt(self) -> bool:
        """Vérifie si une interruption (Ctrl+C) a été demandée."""
        ...

    def get_cursor_column(self) -> int:
        """Retourne la colonne courante du curseur (1-based)."""
        ...
