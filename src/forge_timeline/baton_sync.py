"""BatonSync — keeps the timeline baton and video playhead in lock-step.

See `docs/spec.md` for the full contract.

Wires four signals when ``sync()`` is called:
  - video.position_changed  -> timeline.set_position
  - video.loaded            -> timeline.set_duration
  - timeline.position_clicked -> video.seek
  - timeline.position_dragged -> video.seek

There is no feedback loop because ``TimelineWidget.set_position`` does
not emit any signal — programmatic position updates are silent by design.
"""

from __future__ import annotations

from PySide6.QtCore import QObject

from forge_timeline.timeline import TimelineWidget
from forge_timeline.video_panel import VideoPanel


class BatonSync(QObject):
    def __init__(self, timeline: TimelineWidget, video: VideoPanel) -> None:
        super().__init__(timeline)
        self._timeline = timeline
        self._video = video
        self._enabled = False

    @property
    def enabled(self) -> bool:
        return self._enabled

    def sync(self) -> None:
        if self._enabled:
            return
        self._video.position_changed.connect(self._on_video_position)
        self._video.loaded.connect(self._on_video_loaded)
        self._timeline.position_clicked.connect(self._on_timeline_position)
        self._timeline.position_dragged.connect(self._on_timeline_position)
        self._enabled = True

    def unsync(self) -> None:
        if not self._enabled:
            return
        self._video.position_changed.disconnect(self._on_video_position)
        self._video.loaded.disconnect(self._on_video_loaded)
        self._timeline.position_clicked.disconnect(self._on_timeline_position)
        self._timeline.position_dragged.disconnect(self._on_timeline_position)
        self._enabled = False

    def _on_video_position(self, ms: int) -> None:
        if 0 <= ms <= self._timeline.duration_ms:
            self._timeline.set_position(ms)

    def _on_video_loaded(self, duration_ms: int) -> None:
        self._timeline.set_duration(duration_ms)

    def _on_timeline_position(self, ms: int) -> None:
        self._video.seek(ms)
