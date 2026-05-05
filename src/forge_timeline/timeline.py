"""TimelineWidget — composition root for the layered staves.

See `docs/spec.md` for the full contract.
"""

from __future__ import annotations

from typing import Literal

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

Mode = Literal["canvas", "navigator"]


class TimelineWidget(QWidget):
    position_clicked = Signal(int)
    position_dragged = Signal(int)
    range_selected = Signal(int, int)
    zoom_changed = Signal(float)
    pan_changed = Signal(int)

    def __init__(
        self,
        duration_ms: int,
        mode: Mode = "canvas",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._duration_ms = duration_ms
        self._mode: Mode = mode
        self._position_ms = 0

    @property
    def mode(self) -> Mode:
        return self._mode

    @property
    def duration_ms(self) -> int:
        return self._duration_ms

    def set_position(self, ms: int) -> None:
        raise NotImplementedError

    def set_zoom(self, factor: float, center_ms: int | None = None) -> None:
        raise NotImplementedError

    def set_pan(self, start_ms: int) -> None:
        raise NotImplementedError

    def set_data(
        self,
        *,
        chapters: list[dict] | None = None,
        phrases: list[dict] | None = None,
        curve: list[tuple[int, int]] | None = None,
        thumbnails: list[dict] | None = None,
    ) -> None:
        raise NotImplementedError

    def mark_pending(self, start_ms: int, end_ms: int) -> None:
        raise NotImplementedError

    def mark_built(self, start_ms: int, end_ms: int) -> None:
        raise NotImplementedError
