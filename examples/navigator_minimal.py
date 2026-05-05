"""Minimal navigator-mode demo — empty timeline + baton + precision time label.

Drives the baton across a 10-minute fake duration with a QTimer so first
launch shows real motion. VideoPanel and BatonSync are still stubs and
intentionally not wired here yet.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from forge_timeline import PrecisionTimeLabel, TimelineWidget


def main() -> int:
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("forge-timeline navigator demo")

    central = QWidget()
    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    duration_ms = 600_000
    timeline = TimelineWidget(duration_ms=duration_ms, mode="navigator")
    time_label = PrecisionTimeLabel(ms=0)
    time_label.setStyleSheet(
        "padding: 6px; color: #dddddd; background: #222222; font-size: 14px;"
    )

    layout.addWidget(timeline, stretch=1)
    layout.addWidget(time_label)
    window.setCentralWidget(central)
    window.resize(1000, 240)

    step_ms = 100

    def advance() -> None:
        next_ms = (timeline.position_ms + step_ms) % duration_ms
        timeline.set_position(next_ms)
        time_label.set_ms(next_ms)

    def on_click(ms: int) -> None:
        time_label.set_ms(ms)

    timeline.position_clicked.connect(on_click)
    timeline.position_dragged.connect(on_click)

    timer = QTimer()
    timer.timeout.connect(advance)
    timer.start(50)

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
