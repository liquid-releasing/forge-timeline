"""Canvas-mode demo — same skeleton as navigator demo for now.

In canvas mode the staves (waveform / movement / measure / note /
thumbnail) will eventually paint above the baton. None of those are
implemented yet, so this example currently looks identical to the
navigator demo apart from the mode flag.

Drives the baton with a QTimer so first launch shows motion.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from forge_timeline import PrecisionTimeLabel, TimelineWidget


def main() -> int:
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("forge-timeline canvas demo")

    central = QWidget()
    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    duration_ms = 600_000
    timeline = TimelineWidget(duration_ms=duration_ms, mode="canvas")
    time_label = PrecisionTimeLabel(ms=0)
    time_label.setStyleSheet(
        "padding: 6px; color: #dddddd; background: #222222; font-size: 14px;"
    )

    layout.addWidget(timeline, stretch=1)
    layout.addWidget(time_label)
    window.setCentralWidget(central)
    window.resize(1280, 480)

    position = {"ms": 0}
    step_ms = 100

    def advance() -> None:
        position["ms"] = (position["ms"] + step_ms) % duration_ms
        timeline.set_position(position["ms"])
        time_label.set_ms(position["ms"])

    timer = QTimer()
    timer.timeout.connect(advance)
    timer.start(50)

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
