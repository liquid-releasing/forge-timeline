"""Tests for BatonSync — wire-up between TimelineWidget and VideoPanel.

VideoPanel.seek is the side channel BatonSync drives toward the video.
We patch it on the instance so tests can assert without needing libmpv.
"""

from __future__ import annotations


def test_sync_starts_disabled(qtbot) -> None:
    from forge_timeline import BatonSync, TimelineWidget, VideoPanel

    timeline = TimelineWidget(duration_ms=10_000)
    video = VideoPanel()
    qtbot.addWidget(timeline)
    qtbot.addWidget(video)

    sync = BatonSync(timeline, video)

    assert sync.enabled is False


def test_sync_enables(qtbot) -> None:
    from forge_timeline import BatonSync, TimelineWidget, VideoPanel

    timeline = TimelineWidget(duration_ms=10_000)
    video = VideoPanel()
    qtbot.addWidget(timeline)
    qtbot.addWidget(video)

    sync = BatonSync(timeline, video)
    sync.sync()

    assert sync.enabled is True


def test_sync_is_idempotent(qtbot) -> None:
    from forge_timeline import BatonSync, TimelineWidget, VideoPanel

    timeline = TimelineWidget(duration_ms=10_000)
    video = VideoPanel()
    qtbot.addWidget(timeline)
    qtbot.addWidget(video)

    sync = BatonSync(timeline, video)
    sync.sync()
    sync.sync()

    assert sync.enabled is True


def test_unsync_disables(qtbot) -> None:
    from forge_timeline import BatonSync, TimelineWidget, VideoPanel

    timeline = TimelineWidget(duration_ms=10_000)
    video = VideoPanel()
    qtbot.addWidget(timeline)
    qtbot.addWidget(video)

    sync = BatonSync(timeline, video)
    sync.sync()
    sync.unsync()

    assert sync.enabled is False


def test_video_position_drives_timeline(qtbot) -> None:
    from forge_timeline import BatonSync, TimelineWidget, VideoPanel

    timeline = TimelineWidget(duration_ms=10_000)
    video = VideoPanel()
    qtbot.addWidget(timeline)
    qtbot.addWidget(video)

    BatonSync(timeline, video).sync()

    video.position_changed.emit(5_000)

    assert timeline.position_ms == 5_000


def test_video_loaded_updates_timeline_duration(qtbot) -> None:
    from forge_timeline import BatonSync, TimelineWidget, VideoPanel

    timeline = TimelineWidget(duration_ms=1)
    video = VideoPanel()
    qtbot.addWidget(timeline)
    qtbot.addWidget(video)

    BatonSync(timeline, video).sync()

    video.loaded.emit(180_000)

    assert timeline.duration_ms == 180_000


def test_timeline_click_drives_video_seek(qtbot) -> None:
    from forge_timeline import BatonSync, TimelineWidget, VideoPanel

    timeline = TimelineWidget(duration_ms=10_000)
    video = VideoPanel()
    qtbot.addWidget(timeline)
    qtbot.addWidget(video)

    seeks: list[int] = []
    video.seek = lambda ms: seeks.append(ms)  # type: ignore[method-assign]

    BatonSync(timeline, video).sync()
    timeline.position_clicked.emit(3_000)

    assert seeks == [3_000]


def test_timeline_drag_drives_video_seek(qtbot) -> None:
    from forge_timeline import BatonSync, TimelineWidget, VideoPanel

    timeline = TimelineWidget(duration_ms=10_000)
    video = VideoPanel()
    qtbot.addWidget(timeline)
    qtbot.addWidget(video)

    seeks: list[int] = []
    video.seek = lambda ms: seeks.append(ms)  # type: ignore[method-assign]

    BatonSync(timeline, video).sync()
    timeline.position_dragged.emit(7_500)

    assert seeks == [7_500]


def test_video_position_outside_timeline_duration_is_dropped(qtbot) -> None:
    from forge_timeline import BatonSync, TimelineWidget, VideoPanel

    timeline = TimelineWidget(duration_ms=5_000)
    video = VideoPanel()
    qtbot.addWidget(timeline)
    qtbot.addWidget(video)

    BatonSync(timeline, video).sync()
    timeline.set_position(2_000)

    video.position_changed.emit(99_999)  # past end

    assert timeline.position_ms == 2_000


def test_unsync_disconnects_video_position(qtbot) -> None:
    from forge_timeline import BatonSync, TimelineWidget, VideoPanel

    timeline = TimelineWidget(duration_ms=10_000)
    video = VideoPanel()
    qtbot.addWidget(timeline)
    qtbot.addWidget(video)

    sync = BatonSync(timeline, video)
    sync.sync()
    sync.unsync()

    video.position_changed.emit(5_000)

    assert timeline.position_ms == 0
