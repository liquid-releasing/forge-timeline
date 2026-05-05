"""video_demo.py — full-stack demo with a real video file.

Plays a video in a VideoPanel and shows a BatonSync-coupled timeline +
precision time label below it. Click anywhere on the timeline to seek;
the video and the time label follow. Drag to scrub. Space toggles
play/pause.

Pass the video path on the command line, or omit it to open a file
chooser:

    python examples/video_demo.py
    python examples/video_demo.py path\\to\\video.mp4

Runtime requirements:
  - `python-mpv` Python package (`pip install -e .[mpv]`)
  - `libmpv-2.dll` next to the venv's `python.exe` (forgeplayer ships a copy).
"""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from forge_timeline import (
    BatonSync,
    PrecisionTimeLabel,
    TimelineWidget,
    VideoPanel,
)


def main() -> int:
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("forge-timeline video demo")

    central = QWidget()
    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    video = VideoPanel()
    timeline = TimelineWidget(duration_ms=1, mode="canvas")
    time_label = PrecisionTimeLabel(ms=0)
    time_label.setStyleSheet(
        "padding: 6px; color: #dddddd; background: #222222; font-size: 14px;"
    )

    layout.addWidget(video, stretch=4)
    layout.addWidget(timeline, stretch=1)
    layout.addWidget(time_label)

    window.setCentralWidget(central)
    window.resize(1280, 800)

    sync = BatonSync(timeline, video)
    sync.sync()

    video.position_changed.connect(time_label.set_ms)
    timeline.position_clicked.connect(time_label.set_ms)
    timeline.position_dragged.connect(time_label.set_ms)

    space = QShortcut(QKeySequence(Qt.Key.Key_Space), window)
    space.activated.connect(
        lambda: video.play() if video.is_paused() else video.pause()
    )

    def load_path(path: str) -> None:
        window.setWindowTitle(f"forge-timeline video demo — {path}")
        video.load(path)
        video.play()

    if len(sys.argv) > 1:
        cli_path = sys.argv[1]
        QTimer.singleShot(0, lambda: load_path(cli_path))
    else:
        def pick_then_load() -> None:
            path, _ = QFileDialog.getOpenFileName(
                window,
                "Open a video",
                "",
                "Video files (*.mp4 *.mkv *.mov *.webm *.avi);;All files (*.*)",
            )
            if path:
                load_path(path)
            else:
                window.close()

        QTimer.singleShot(0, pick_then_load)

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
