"""BatonSync — keeps the timeline baton and video playhead in lock-step.

See `docs/spec.md` for the full contract.
"""

from __future__ import annotations

from forge_timeline.timeline import TimelineWidget
from forge_timeline.video_panel import VideoPanel


class BatonSync:
    def __init__(self, timeline: TimelineWidget, video: VideoPanel) -> None:
        self._timeline = timeline
        self._video = video
        self._enabled = False

    @property
    def enabled(self) -> bool:
        return self._enabled

    def sync(self) -> None:
        raise NotImplementedError

    def unsync(self) -> None:
        raise NotImplementedError
