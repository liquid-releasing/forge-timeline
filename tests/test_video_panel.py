"""Tests for VideoPanel — exercise everything that does not require libmpv.

VideoPanel lazy-imports `mpv` on first showEvent. These tests construct
the widget but never show it, so libmpv-2.dll is not required for the
test suite to pass.
"""

from __future__ import annotations


def test_constructs_without_libmpv(qtbot) -> None:
    from forge_timeline import VideoPanel

    panel = VideoPanel()
    qtbot.addWidget(panel)

    assert panel.position_ms() == 0
    assert panel.duration_ms() == 0
    assert panel.is_paused() is True


def test_seek_before_init_is_noop(qtbot) -> None:
    from forge_timeline import VideoPanel

    panel = VideoPanel()
    qtbot.addWidget(panel)

    panel.seek(5_000)

    assert panel.position_ms() == 0


def test_load_before_init_queues_pending(qtbot) -> None:
    from forge_timeline import VideoPanel

    panel = VideoPanel()
    qtbot.addWidget(panel)

    panel.load("/path/to/some.mp4")

    assert panel._pending_load == "/path/to/some.mp4"


def test_play_before_init_arms_autoplay(qtbot) -> None:
    from forge_timeline import VideoPanel

    panel = VideoPanel()
    qtbot.addWidget(panel)

    panel.play()

    assert panel._autoplay_after_load is True


def test_pause_before_init_disarms_autoplay(qtbot) -> None:
    from forge_timeline import VideoPanel

    panel = VideoPanel()
    qtbot.addWidget(panel)

    panel.play()
    panel.pause()

    assert panel._autoplay_after_load is False


def test_terminate_is_idempotent(qtbot) -> None:
    from forge_timeline import VideoPanel

    panel = VideoPanel()
    qtbot.addWidget(panel)

    panel.terminate()
    panel.terminate()

    assert panel._mpv is None
