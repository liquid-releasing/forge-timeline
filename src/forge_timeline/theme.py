"""Theme — design tokens for forge-timeline.

Defaults match the forge family dark baseline. Consumers override by
constructing a `Theme` and passing it to `TimelineWidget(..., theme=...)`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtGui import QColor


@dataclass(frozen=True)
class Theme:
    background: QColor = field(default_factory=lambda: QColor("#1a1a1a"))
    panel: QColor = field(default_factory=lambda: QColor("#222222"))
    grid: QColor = field(default_factory=lambda: QColor("#333333"))
    text: QColor = field(default_factory=lambda: QColor("#dddddd"))
    text_muted: QColor = field(default_factory=lambda: QColor("#888888"))
    baton: QColor = field(default_factory=lambda: QColor("#ffaa00"))
    selection: QColor = field(default_factory=lambda: QColor(255, 170, 0, 64))
    waveform: QColor = field(default_factory=lambda: QColor("#4488cc"))
    curve: QColor = field(default_factory=lambda: QColor("#88dd88"))
    pending: QColor = field(default_factory=lambda: QColor("#444444"))
    divergence: QColor = field(default_factory=lambda: QColor("#cc4444"))


DEFAULT_THEME = Theme()
