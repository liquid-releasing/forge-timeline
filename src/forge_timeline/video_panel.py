"""VideoPanel — libmpv-backed video preview widget.

See `docs/spec.md` for the full contract.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget


class VideoPanel(QWidget):
    position_changed = Signal(int)
    loaded = Signal(int)
    ended = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

    def load(self, path: str | Path) -> None:
        raise NotImplementedError

    def play(self) -> None:
        raise NotImplementedError

    def pause(self) -> None:
        raise NotImplementedError

    def seek(self, ms: int) -> None:
        raise NotImplementedError

    def position_ms(self) -> int:
        raise NotImplementedError

    def duration_ms(self) -> int:
        raise NotImplementedError
