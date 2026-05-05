"""ThumbnailStaff — video frames sampled at staff width."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget


class ThumbnailStaff(QWidget):
    def __init__(self, duration_ms: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._duration_ms = duration_ms

    def set_thumbnails(self, thumbnails: list[dict]) -> None:
        raise NotImplementedError
