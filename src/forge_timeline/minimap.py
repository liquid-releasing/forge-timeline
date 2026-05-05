"""MiniMap — compressed full-file overview strip with viewport rectangle.

See `docs/spec.md` for the full contract.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget


class MiniMap(QWidget):
    viewport_changed = Signal(int, int)
    position_clicked = Signal(int)

    def __init__(self, duration_ms: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._duration_ms = duration_ms

    def set_viewport(self, start_ms: int, end_ms: int) -> None:
        raise NotImplementedError

    def set_chapters(self, chapters: list[dict]) -> None:
        raise NotImplementedError
