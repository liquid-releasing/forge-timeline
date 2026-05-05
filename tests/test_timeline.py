"""Tests for TimelineWidget."""

from __future__ import annotations

import pytest


def test_default_state(qtbot) -> None:
    from forge_timeline import TimelineWidget

    widget = TimelineWidget(duration_ms=60_000)
    qtbot.addWidget(widget)

    assert widget.duration_ms == 60_000
    assert widget.position_ms == 0
    assert widget.mode == "canvas"


def test_navigator_mode(qtbot) -> None:
    from forge_timeline import TimelineWidget

    widget = TimelineWidget(duration_ms=60_000, mode="navigator")
    qtbot.addWidget(widget)

    assert widget.mode == "navigator"


def test_zero_duration_rejected(qtbot) -> None:
    from forge_timeline import TimelineWidget

    with pytest.raises(ValueError):
        TimelineWidget(duration_ms=0)


def test_negative_duration_rejected(qtbot) -> None:
    from forge_timeline import TimelineWidget

    with pytest.raises(ValueError):
        TimelineWidget(duration_ms=-1)


def test_set_position_updates_property(qtbot) -> None:
    from forge_timeline import TimelineWidget

    widget = TimelineWidget(duration_ms=60_000)
    qtbot.addWidget(widget)

    widget.set_position(15_000)
    assert widget.position_ms == 15_000

    widget.set_position(60_000)
    assert widget.position_ms == 60_000


@pytest.mark.parametrize("bad_ms", [-1, 60_001])
def test_set_position_out_of_range_rejected(qtbot, bad_ms: int) -> None:
    from forge_timeline import TimelineWidget

    widget = TimelineWidget(duration_ms=60_000)
    qtbot.addWidget(widget)

    with pytest.raises(ValueError):
        widget.set_position(bad_ms)


def test_paints_without_crashing(qtbot) -> None:
    from forge_timeline import TimelineWidget

    widget = TimelineWidget(duration_ms=600_000)
    qtbot.addWidget(widget)
    widget.resize(800, 100)
    widget.set_position(123_456)

    widget.show()
    qtbot.waitExposed(widget)


def test_pick_tick_interval_picks_smaller_for_short_duration() -> None:
    from forge_timeline.timeline import _pick_tick_interval

    assert _pick_tick_interval(ms_per_pixel=1.0) == 100
    assert _pick_tick_interval(ms_per_pixel=10.0) == 1_000
    assert _pick_tick_interval(ms_per_pixel=100.0) == 10_000
    assert _pick_tick_interval(ms_per_pixel=10_000.0) == 1_800_000
