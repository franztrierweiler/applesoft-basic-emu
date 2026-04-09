"""Implémentation CLI de l'IOBridge.

Utilise stdin/stdout pour les I/O.
"""

from __future__ import annotations

import os
import signal
import sys
import time

# Limite de taille pour LOAD (SEC-BP-25)
_MAX_FILE_SIZE = 1_048_576  # 1 Mo


class IOBridgeCLI:
    """IOBridge pour le terminal CLI."""

    def __init__(self):
        self._interrupted = False
        self._cursor_column = 1
        self._video_mode: str = "normal"
        self._speed: int = 0
        self._last_key: int = 0  # Dernière touche (RG-0011, $C000)
        self._install_sigint_handler()

    def set_video_mode(self, mode: str) -> None:
        """Définit le mode vidéo : normal, inverse, flash."""
        self._video_mode = mode

    def set_speed(self, value: int) -> None:
        """Définit le délai entre caractères (0-255)."""
        self._speed = value

    def print_str(self, text: str) -> None:
        """Affiche une chaîne sur stdout avec mode vidéo et vitesse."""
        if self._speed > 0 and text and text != "\n":
            for ch in text:
                self._write_char(ch)
                if ch != "\n":
                    time.sleep(self._speed / 1000.0)
        else:
            self._write_styled(text)
        # Mettre à jour la position du curseur
        if "\n" in text:
            last_line = text.rsplit("\n", 1)[-1]
            self._cursor_column = len(last_line) + 1
        else:
            self._cursor_column += len(text)

    def _write_char(self, ch: str) -> None:
        """Écrit un caractère avec le style vidéo courant."""
        self._write_styled(ch)

    def _write_styled(self, text: str) -> None:
        """Écrit du texte avec les codes ANSI du mode vidéo courant."""
        if not text:
            return
        if self._video_mode == "inverse":
            sys.stdout.write(f"\033[7m{text}\033[0m")
        elif self._video_mode == "flash":
            sys.stdout.write(f"\033[5m{text}\033[0m")
        else:
            sys.stdout.write(text)
        sys.stdout.flush()

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

    def move_cursor_to_row(self, row: int) -> None:
        """Déplace le curseur à la ligne row (1-based) avec ANSI."""
        sys.stdout.write(f"\033[{row};1H")
        sys.stdout.flush()
        self._cursor_column = 1

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

    def _install_sigint_handler(self) -> None:
        """Installe le handler SIGINT pour Ctrl+C (UC-024)."""

        def _sigint_handler(signum, frame):
            self._interrupted = True

        signal.signal(signal.SIGINT, _sigint_handler)

    def get_cursor_column(self) -> int:
        """Retourne la colonne courante du curseur."""
        return self._cursor_column

    def get_last_key(self) -> int:
        """Retourne la dernière touche pressée (RG-0011, $C000)."""
        return self._last_key

    def set_last_key(self, key: int) -> None:
        """Définit la dernière touche pressée."""
        self._last_key = key

    # --- Persistance fichier (UC-004, UC-005) ---

    def save_file(self, filename: str, content: str, base_dir: str | None = None) -> None:
        """Sauvegarde du contenu dans un fichier (SEC-BP-22, SEC-BP-25)."""
        from .errors import BasicError

        path = self._resolve_safe_path(filename, base_dir)
        if len(content.encode("utf-8")) > _MAX_FILE_SIZE:
            raise BasicError(258)  # FILE TOO LARGE
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def load_file(self, filename: str, base_dir: str | None = None) -> str:
        """Charge un fichier texte (SEC-BP-22, SEC-BP-23, SEC-BP-25)."""
        from .errors import BasicError

        path = self._resolve_safe_path(filename, base_dir)
        if not os.path.exists(path):
            raise BasicError(256)  # FILE NOT FOUND
        size = os.path.getsize(path)
        if size > _MAX_FILE_SIZE:
            raise BasicError(258)  # FILE TOO LARGE
        with open(path, encoding="utf-8") as f:
            return f.read()

    def _resolve_safe_path(self, filename: str, base_dir: str | None = None) -> str:
        """Résout un chemin sûr (SEC-BP-22 : restriction au répertoire de base)."""
        from .errors import BasicError

        if base_dir is None:
            base_dir = os.getcwd()
        base = os.path.realpath(base_dir)
        target = os.path.realpath(os.path.join(base, filename))
        if not target.startswith(base + os.sep) and target != base:
            raise BasicError(257)  # PATH NOT ALLOWED
        return target
