"""TimelineWidget — composition root for the layered staves.

See `docs/spec.md` for the full contract.
"""

from __future__ import annotations

from typing import Literal

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QWidget

from forge_timeline.theme import DEFAULT_THEME, Theme
from forge_timeline.time_format import format_time

Mode = Literal["canvas", "navigator"]

_TICK_INTERVALS = (
    100, 500, 1_000, 5_000, 10_000, 30_000, 60_000,
    300_000, 600_000, 1_800_000, 3_600_000,
)


def _pick_tick_interval(ms_per_pixel: float, target_pixel_spacing: int = 100) -> int:
    """Return the smallest tick interval whose pixel spacing >= target."""
    for interval in _TICK_INTERVALS:
        if interval / ms_per_pixel >= target_pixel_spacing:
            return interval
    return _TICK_INTERVALS[-1]


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
        theme: Theme | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        if duration_ms <= 0:
            raise ValueError(f"duration_ms must be positive, got {duration_ms}")
        self._duration_ms = duration_ms
        self._mode: Mode = mode
        self._position_ms = 0
        self._theme = theme or DEFAULT_THEME
        self.setMinimumHeight(64)

    @property
    def mode(self) -> Mode:
        return self._mode

    @property
    def duration_ms(self) -> int:
        return self._duration_ms

    @property
    def position_ms(self) -> int:
        return self._position_ms

    def set_position(self, ms: int) -> None:
        if not 0 <= ms <= self._duration_ms:
            raise ValueError(
                f"position {ms} out of range [0, {self._duration_ms}]"
            )
        if self._position_ms != ms:
            self._position_ms = ms
            self.update()

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

    def _x_to_ms(self, x: float) -> int:
        width = self.width()
        if width <= 0:
            return 0
        fraction = max(0.0, min(1.0, x / width))
        return int(fraction * self._duration_ms)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            ms = self._x_to_ms(event.position().x())
            self.set_position(ms)
            self.position_clicked.emit(ms)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton:
            ms = self._x_to_ms(event.position().x())
            self.set_position(ms)
            self.position_dragged.emit(ms)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        rect = self.rect()
        width = rect.width()
        height = rect.height()

        painter.fillRect(rect, self._theme.background)

        if width <= 0 or height <= 0:
            return

        ms_per_pixel = self._duration_ms / width
        interval = _pick_tick_interval(ms_per_pixel)

        grid_pen = QPen(self._theme.grid)
        grid_pen.setWidth(1)
        painter.setPen(grid_pen)
        tick = 0
        while tick <= self._duration_ms:
            x = int(tick / self._duration_ms * width)
            painter.drawLine(x, 0, x, height)
            tick += interval

        painter.setPen(self._theme.text_muted)
        tick = 0
        while tick <= self._duration_ms:
            x = int(tick / self._duration_ms * width)
            painter.drawText(x + 4, 14, format_time(tick))
            tick += interval

        baton_pen = QPen(self._theme.baton)
        baton_pen.setWidth(2)
        painter.setPen(baton_pen)
        baton_x = int(self._position_ms / self._duration_ms * width)
        painter.drawLine(baton_x, 0, baton_x, height)
