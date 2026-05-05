"""Baton — vertical playhead line spanning all staves.

See `docs/spec.md` for the full contract.
"""

from __future__ import annotations

from PySide6.QtWidgets import QWidget


class Baton(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

    def set_position_ms(self, ms: int) -> None:
        raise NotImplementedError
