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
    frame_step_requested = Signal(int)  # +1 forward, -1 back — emitted on Shift+click

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
        self._waveform_peaks: list[float] = []
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

    def set_duration(self, ms: int) -> None:
        if ms <= 0:
            raise ValueError(f"duration_ms must be positive, got {ms}")
        if self._duration_ms == ms:
            return
        self._duration_ms = ms
        if self._position_ms > ms:
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
        waveform: list[float] | None = None,
    ) -> None:
        if any(x is not None for x in (chapters, phrases, curve, thumbnails)):
            raise NotImplementedError(
                "set_data: chapters/phrases/curve/thumbnails are not yet wired; "
                "only waveform is rendered in v0"
            )
        if waveform is not None:
            self._waveform_peaks = list(waveform)
            self.update()

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
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                # Shift+click: jog one frame in the direction of the click
                # relative to the current baton position. Acts as a shuttle
                # control without leaving the timeline.
                if ms > self._position_ms:
                    self.frame_step_requested.emit(1)
                elif ms < self._position_ms:
                    self.frame_step_requested.emit(-1)
                event.accept()
                return
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

        if self._waveform_peaks:
            self._paint_waveform(painter, width, height)

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

    def _paint_waveform(self, painter: QPainter, width: int, height: int) -> None:
        peak_count = len(self._waveform_peaks)
        band_top = 18
        band_h = max(20, int(height * 0.55))
        center = band_top + band_h // 2
        half_h = band_h // 2
        painter.setPen(self._theme.waveform)
        for col in range(width):
            peak_idx = int(col / width * peak_count)
            if peak_idx >= peak_count:
                break
            peak = self._waveform_peaks[peak_idx]
            h = int(peak * half_h)
            if h > 0:
                painter.drawLine(col, center - h, col, center + h)
