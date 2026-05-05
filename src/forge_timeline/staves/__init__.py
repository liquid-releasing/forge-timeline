"""Staff widgets — one per row in the canvas-mode track stack."""

from __future__ import annotations

from forge_timeline.staves.measure import MeasureStaff
from forge_timeline.staves.movement import MovementStaff
from forge_timeline.staves.note import NoteStaff
from forge_timeline.staves.thumbnail import ThumbnailStaff
from forge_timeline.staves.waveform import WaveformStaff

__all__ = [
    "MeasureStaff",
    "MovementStaff",
    "NoteStaff",
    "ThumbnailStaff",
    "WaveformStaff",
]
