"""NoteStaff — funscript curve as sparkline."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget


class NoteStaff(QWidget):
    def __init__(self, duration_ms: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._duration_ms = duration_ms

    def set_curve(self, curve: list[tuple[int, int]]) -> None:
        raise NotImplementedError
