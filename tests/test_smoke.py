"""Smoke tests — package imports and the implemented helpers round-trip."""

from __future__ import annotations

import pytest


def test_package_imports() -> None:
    from forge_timeline import (
        BatonSync,
        TimelineWidget,
        VideoPanel,
        __version__,
        format_time,
        parse_time,
    )

    assert __version__
    assert all(callable(x) for x in (format_time, parse_time))
    assert all(isinstance(x, type) for x in (BatonSync, TimelineWidget, VideoPanel))


@pytest.mark.parametrize(
    ("ms", "expected"),
    [
        (0, "00:00:00.000"),
        (1, "00:00:00.001"),
        (1_000, "00:00:01.000"),
        (61_500, "00:01:01.500"),
        (3_661_001, "01:01:01.001"),
        (35_999_999, "09:59:59.999"),
    ],
)
def test_format_time(ms: int, expected: str) -> None:
    from forge_timeline import format_time

    assert format_time(ms) == expected


def test_format_time_rejects_negative() -> None:
    from forge_timeline import format_time

    with pytest.raises(ValueError):
        format_time(-1)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("00:00:00.000", 0),
        ("00:00:00", 0),
        ("00:00:01.500", 1_500),
        ("00:00:01.5", 1_500),
        ("01:01:01.001", 3_661_001),
        ("  00:01:00  ", 60_000),
    ],
)
def test_parse_time(text: str, expected: int) -> None:
    from forge_timeline import parse_time

    assert parse_time(text) == expected


@pytest.mark.parametrize("bad", ["", "1:2", "00:60:00", "00:00:60", "abc"])
def test_parse_time_rejects_garbage(bad: str) -> None:
    from forge_timeline import parse_time

    with pytest.raises(ValueError):
        parse_time(bad)


@pytest.mark.parametrize("ms", [0, 1, 999, 1_000, 60_000, 3_600_000, 35_999_999])
def test_round_trip(ms: int) -> None:
    from forge_timeline import format_time, parse_time

    assert parse_time(format_time(ms)) == ms
