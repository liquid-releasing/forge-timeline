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


def test_set_duration_updates_property(qtbot) -> None:
    from forge_timeline import TimelineWidget

    widget = TimelineWidget(duration_ms=60_000)
    qtbot.addWidget(widget)

    widget.set_duration(120_000)

    assert widget.duration_ms == 120_000


def test_set_duration_clamps_position_when_shrinking(qtbot) -> None:
    from forge_timeline import TimelineWidget

    widget = TimelineWidget(duration_ms=60_000)
    qtbot.addWidget(widget)

    widget.set_position(50_000)
    widget.set_duration(30_000)

    assert widget.duration_ms == 30_000
    assert widget.position_ms == 30_000


def test_set_duration_keeps_position_when_growing(qtbot) -> None:
    from forge_timeline import TimelineWidget

    widget = TimelineWidget(duration_ms=60_000)
    qtbot.addWidget(widget)

    widget.set_position(30_000)
    widget.set_duration(120_000)

    assert widget.duration_ms == 120_000
    assert widget.position_ms == 30_000


def test_set_duration_zero_rejected(qtbot) -> None:
    from forge_timeline import TimelineWidget

    widget = TimelineWidget(duration_ms=60_000)
    qtbot.addWidget(widget)

    with pytest.raises(ValueError):
        widget.set_duration(0)


def test_left_click_emits_and_updates_position(qtbot) -> None:
    """Left-click anywhere fires position_clicked and updates position_ms in lockstep.

    Exact ms-from-pixel calibration is verified by the _x_to_ms unit tests; this
    test only checks the integration (signal fires, position updates, value
    falls inside the duration range).
    """
    from PySide6.QtCore import QPoint, Qt

    from forge_timeline import TimelineWidget

    widget = TimelineWidget(duration_ms=1_000)
    qtbot.addWidget(widget)
    widget.resize(200, 80)
    widget.show()
    qtbot.waitExposed(widget)

    with qtbot.waitSignal(widget.position_clicked, timeout=1_000) as blocker:
        qtbot.mouseClick(widget, Qt.MouseButton.LeftButton, pos=QPoint(100, 40))

    emitted_ms = blocker.args[0]
    assert 0 <= emitted_ms <= 1_000
    assert widget.position_ms == emitted_ms


def test_left_click_at_left_edge_seeks_to_zero(qtbot) -> None:
    from PySide6.QtCore import QPoint, Qt

    from forge_timeline import TimelineWidget

    widget = TimelineWidget(duration_ms=1_000)
    qtbot.addWidget(widget)
    widget.resize(200, 80)
    widget.show()
    qtbot.waitExposed(widget)

    with qtbot.waitSignal(widget.position_clicked, timeout=1_000) as blocker:
        qtbot.mouseClick(widget, Qt.MouseButton.LeftButton, pos=QPoint(0, 40))

    assert blocker.args == [0]
    assert widget.position_ms == 0


def test_drag_emits_position_dragged_and_updates(qtbot) -> None:
    """Drag with left button held fires position_dragged in lockstep with position_ms."""
    from PySide6.QtCore import QPoint, Qt

    from forge_timeline import TimelineWidget

    widget = TimelineWidget(duration_ms=1_000)
    qtbot.addWidget(widget)
    widget.resize(200, 80)
    widget.show()
    qtbot.waitExposed(widget)

    with qtbot.waitSignal(widget.position_dragged, timeout=1_000) as blocker:
        qtbot.mousePress(widget, Qt.MouseButton.LeftButton, pos=QPoint(40, 40))
        qtbot.mouseMove(widget, pos=QPoint(140, 40))
        qtbot.mouseRelease(widget, Qt.MouseButton.LeftButton, pos=QPoint(140, 40))

    emitted_ms = blocker.args[0]
    assert 0 <= emitted_ms <= 1_000
    assert widget.position_ms == emitted_ms


def test_right_click_does_not_seek(qtbot) -> None:
    from PySide6.QtCore import QPoint, Qt

    from forge_timeline import TimelineWidget

    widget = TimelineWidget(duration_ms=1_000)
    qtbot.addWidget(widget)
    widget.resize(200, 80)
    widget.show()
    qtbot.waitExposed(widget)

    qtbot.mouseClick(widget, Qt.MouseButton.RightButton, pos=QPoint(100, 40))

    assert widget.position_ms == 0


def test_x_to_ms_midpoint(qtbot) -> None:
    from forge_timeline import TimelineWidget

    widget = TimelineWidget(duration_ms=1_000)
    qtbot.addWidget(widget)
    widget.resize(1_000, 80)

    assert widget._x_to_ms(500) == 500


def test_x_to_ms_at_zero(qtbot) -> None:
    from forge_timeline import TimelineWidget

    widget = TimelineWidget(duration_ms=1_000)
    qtbot.addWidget(widget)
    widget.resize(1_000, 80)

    assert widget._x_to_ms(0) == 0


def test_x_to_ms_at_full_width(qtbot) -> None:
    from forge_timeline import TimelineWidget

    widget = TimelineWidget(duration_ms=1_000)
    qtbot.addWidget(widget)
    widget.resize(1_000, 80)

    assert widget._x_to_ms(1_000) == 1_000


def test_x_to_ms_clamps_negative(qtbot) -> None:
    from forge_timeline import TimelineWidget

    widget = TimelineWidget(duration_ms=1_000)
    qtbot.addWidget(widget)
    widget.resize(100, 50)

    assert widget._x_to_ms(-50) == 0


def test_x_to_ms_clamps_overflow(qtbot) -> None:
    from forge_timeline import TimelineWidget

    widget = TimelineWidget(duration_ms=1_000)
    qtbot.addWidget(widget)
    widget.resize(100, 50)

    assert widget._x_to_ms(150) == 1_000
