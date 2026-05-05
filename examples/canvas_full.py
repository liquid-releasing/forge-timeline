"""Full canvas-mode demo — FunscriptForge / beatflo-shape.

Shows: video panel + full-stack canvas timeline (mini-map, waveform,
movement staff, measure staff, note staff, thumbnails, baton), synced
via BatonSync.

Status: skeleton only. Will not run end-to-end until staves and
VideoPanel are implemented.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter

from forge_timeline import BatonSync, TimelineWidget, VideoPanel


def main() -> int:
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("forge-timeline canvas demo")

    splitter = QSplitter(Qt.Orientation.Vertical)
    video = VideoPanel()
    timeline = TimelineWidget(duration_ms=600_000, mode="canvas")

    splitter.addWidget(video)
    splitter.addWidget(timeline)
    splitter.setStretchFactor(0, 3)
    splitter.setStretchFactor(1, 2)
    window.setCentralWidget(splitter)

    sync = BatonSync(timeline, video)
    sync.sync()

    window.resize(1280, 800)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
