"""Tests for PrecisionTimeLabel."""

from __future__ import annotations

import pytest


def test_default_text_is_zero(qtbot) -> None:
    from forge_timeline import PrecisionTimeLabel

    label = PrecisionTimeLabel()
    qtbot.addWidget(label)

    assert label.text() == "00:00:00.000"
    assert label.position_ms == 0


@pytest.mark.parametrize(
    ("ms", "expected"),
    [
        (0, "00:00:00.000"),
        (1, "00:00:00.001"),
        (1_000, "00:00:01.000"),
        (61_500, "00:01:01.500"),
        (3_661_001, "01:01:01.001"),
    ],
)
def test_set_ms_updates_text_and_position(qtbot, ms: int, expected: str) -> None:
    from forge_timeline import PrecisionTimeLabel

    label = PrecisionTimeLabel()
    qtbot.addWidget(label)

    label.set_ms(ms)

    assert label.text() == expected
    assert label.position_ms == ms


def test_construction_with_initial_ms(qtbot) -> None:
    from forge_timeline import PrecisionTimeLabel

    label = PrecisionTimeLabel(ms=5_000)
    qtbot.addWidget(label)

    assert label.text() == "00:00:05.000"
    assert label.position_ms == 5_000


def test_negative_ms_raises_through_format_time(qtbot) -> None:
    from forge_timeline import PrecisionTimeLabel

    label = PrecisionTimeLabel()
    qtbot.addWidget(label)

    with pytest.raises(ValueError):
        label.set_ms(-1)


def test_font_is_monospace(qtbot) -> None:
    from forge_timeline import PrecisionTimeLabel

    label = PrecisionTimeLabel()
    qtbot.addWidget(label)

    assert label.font().fixedPitch()
