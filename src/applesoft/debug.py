"""Traceur debug pour l'interpréteur Applesoft BASIC.

Affiche la trace d'exécution sur stderr pour ne pas interférer
avec la sortie BASIC. Activable par --debug (CLI) ou DEBUG ON/OFF (REPL).
"""

from __future__ import annotations

import sys


class DebugTracer:
    """Mode debug : trace d'exécution."""

    def __init__(self):
        self._enabled = False

    @property
    def enabled(self) -> bool:
        return self._enabled

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def trace(self, line_num: int, stmt_text: str, variables: dict | None = None) -> None:
        """Affiche la trace d'une instruction sur stderr."""
        if not self._enabled:
            return
        msg = f"[DEBUG] {line_num}: {stmt_text}"
        if variables:
            vars_str = ", ".join(f"{k}={v}" for k, v in variables.items())
            msg += f"  | {vars_str}"
        print(msg, file=sys.stderr)
