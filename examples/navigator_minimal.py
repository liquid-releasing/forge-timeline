"""Minimal navigator-mode demo — forgeplayer-shape.

Shows: video panel + read-only timeline (movement staff + baton only),
synced via BatonSync.

Status: skeleton only. Will not run end-to-end until staves and
VideoPanel are implemented.
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from forge_timeline import BatonSync, TimelineWidget, VideoPanel


def main() -> int:
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("forge-timeline navigator demo")
    central = QWidget()
    layout = QVBoxLayout(central)

    video = VideoPanel()
    timeline = TimelineWidget(duration_ms=600_000, mode="navigator")

    layout.addWidget(video, stretch=4)
    layout.addWidget(timeline, stretch=1)
    window.setCentralWidget(central)

    sync = BatonSync(timeline, video)
    sync.sync()

    window.resize(960, 600)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
