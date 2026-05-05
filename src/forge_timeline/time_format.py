"""HH:MM:SS.mmm precision time formatting and parsing.

Pure helpers used everywhere editor UIs need to display or accept a
millisecond-precise timestamp. No Qt dependency.
"""

from __future__ import annotations

import re

_PATTERN = re.compile(r"^(\d+):([0-5]?\d):([0-5]?\d)(?:\.(\d{1,3}))?$")


def format_time(ms: int) -> str:
    """Format a non-negative millisecond count as ``HH:MM:SS.mmm``."""
    if ms < 0:
        raise ValueError(f"ms must be non-negative, got {ms}")
    total_seconds, millis = divmod(int(ms), 1000)
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d}"


def parse_time(text: str) -> int:
    """Parse ``HH:MM:SS.mmm`` (or ``HH:MM:SS``) into milliseconds.

    Sub-second precision shorter than three digits is right-padded:
    ``"0:00:01.5"`` -> ``1500``.
    """
    m = _PATTERN.match(text.strip())
    if not m:
        raise ValueError(f"invalid time format: {text!r}")
    h, mn, s, frac = m.groups()
    millis = int(frac.ljust(3, "0")) if frac else 0
    return ((int(h) * 60 + int(mn)) * 60 + int(s)) * 1000 + millis
