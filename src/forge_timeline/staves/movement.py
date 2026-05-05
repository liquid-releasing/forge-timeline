"""MovementStaff — chapter bands with name, content_type chip, build state."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget


class MovementStaff(QWidget):
    chapter_clicked = Signal(int)

    def __init__(self, duration_ms: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._duration_ms = duration_ms

    def set_chapters(self, chapters: list[dict]) -> None:
        raise NotImplementedError
