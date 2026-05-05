"""PrecisionTimeLabel — QLabel that shows HH:MM:SS.mmm time.

Used at the baton, in status bars, and anywhere an editor surface needs
to display a millisecond-precise position. Monospace font so digits do
not jiggle as the value updates.
"""

from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QWidget

from forge_timeline.time_format import format_time


class PrecisionTimeLabel(QLabel):
    def __init__(self, ms: int = 0, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        font = QFont()
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setFixedPitch(True)
        self.setFont(font)
        self._ms = 0
        self.set_ms(ms)

    def set_ms(self, ms: int) -> None:
        self._ms = ms
        self.setText(format_time(ms))

    @property
    def position_ms(self) -> int:
        return self._ms
