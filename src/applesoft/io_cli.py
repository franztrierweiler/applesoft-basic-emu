"""Implémentation CLI de l'IOBridge.

Utilise stdin/stdout pour les I/O.
"""

from __future__ import annotations

import sys


class IOBridgeCLI:
    """IOBridge pour le terminal CLI."""

    def __init__(self):
        self._interrupted = False
        self._cursor_column = 1

    def print_str(self, text: str) -> None:
        """Affiche une chaîne sur stdout."""
        sys.stdout.write(text)
        sys.stdout.flush()
        # Mettre à jour la position du curseur
        if "\n" in text:
            # Après un retour à la ligne, on est en colonne 1
            last_line = text.rsplit("\n", 1)[-1]
            self._cursor_column = len(last_line) + 1
        else:
            self._cursor_column += len(text)

    def input_str(self, prompt: str = "") -> str:
        """Lit une ligne sur stdin."""
        if prompt:
            self.print_str(prompt)
        line = input()
        self._cursor_column = 1
        return line

    def get_char(self) -> str:
        """Lit un caractère sans écho."""
        # En mode CLI basique, on lit une ligne et on prend le premier caractère
        line = input()
        self._cursor_column = 1
        return line[0] if line else ""

    def clear_screen(self) -> None:
        """Efface l'écran avec les codes ANSI."""
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()
        self._cursor_column = 1

    def check_interrupt(self) -> bool:
        """Vérifie le flag d'interruption."""
        if self._interrupted:
            self._interrupted = False
            return True
        return False

    def set_interrupted(self) -> None:
        """Signale une interruption Ctrl+C."""
        self._interrupted = True

    def get_cursor_column(self) -> int:
        """Retourne la colonne courante du curseur."""
        return self._cursor_column
