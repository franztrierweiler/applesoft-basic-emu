"""Fixtures pytest partagées pour les tests de l'émulateur Applesoft BASIC."""

from __future__ import annotations

import pytest


class MockIOBridge:
    """IOBridge mock pour les tests — capture les sorties, simule les entrées."""

    def __init__(self) -> None:
        self.output_buffer: list[str] = []
        self.input_queue: list[str] = []
        self.get_queue: list[str] = []

    def output(self, text: str) -> None:
        """Capture la sortie texte."""
        self.output_buffer.append(text)

    def get_output(self) -> str:
        """Retourne toute la sortie capturée."""
        return "".join(self.output_buffer)

    def input(self, prompt: str = "") -> str:
        """Retourne la prochaine entrée simulée."""
        if self.input_queue:
            return self.input_queue.pop(0)
        return ""

    def get(self) -> str:
        """Retourne le prochain caractère simulé (GET)."""
        if self.get_queue:
            return self.get_queue.pop(0)
        return ""

    def home(self) -> None:
        """Efface l'écran (no-op en test)."""

    def render_gr(self, buffer: list[int]) -> None:
        """Rendu GR (no-op en test)."""

    def render_hgr(self, buffer: list[int]) -> None:
        """Rendu HGR (no-op en test)."""

    def save(self, name: str, content: str) -> None:
        """Sauvegarde (no-op en test)."""

    def load(self, name: str) -> str:
        """Chargement (stub en test)."""
        return ""


@pytest.fixture
def mock_io() -> MockIOBridge:
    """Fournit un IOBridge mock pour les tests."""
    return MockIOBridge()
