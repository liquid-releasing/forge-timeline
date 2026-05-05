"""VideoPanel — libmpv-backed video preview widget.

See `docs/spec.md` for the full contract.

Construction is cheap and does not require libmpv. The libmpv binary is
loaded lazily on first showEvent — `forge_timeline` itself imports
cleanly without `libmpv-2.dll` available, so consumers that only want
the timeline canvas pay no cost.

Runtime requirements when the panel is shown:
  - `python-mpv` Python package (available via the `[mpv]` extra)
  - `libmpv-2.dll` (Windows) findable on PATH or in the venv's
    Scripts directory. forgeplayer's repo ships a working copy.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QCloseEvent, QShowEvent
from PySide6.QtWidgets import QWidget

_POLL_MS = 100

_libmpv_search_done = False


def _ensure_libmpv_findable() -> None:
    """Add likely libmpv-2.dll locations to the DLL search path.

    python-mpv calls ctypes.CDLL("libmpv-2.dll"), which on Windows resolves
    via Windows' DLL search. When the venv is activated, .venv/Scripts/ is
    on PATH and the lookup works; when python.exe is invoked directly, it
    is not. Probe the directory next to python.exe and add it via
    os.add_dll_directory (Python 3.8+) plus PATH for the older fallback.
    Idempotent.
    """
    global _libmpv_search_done
    if _libmpv_search_done:
        return
    candidates = [Path(sys.executable).parent]
    for candidate in candidates:
        dll = candidate / "libmpv-2.dll"
        if dll.exists():
            if hasattr(os, "add_dll_directory"):
                os.add_dll_directory(str(candidate))
            os.environ["PATH"] = str(candidate) + os.pathsep + os.environ.get("PATH", "")
    _libmpv_search_done = True


class VideoPanel(QWidget):
    position_changed = Signal(int)
    loaded = Signal(int)
    ended = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow)
        self.setStyleSheet("background-color: black;")
        self.setMinimumSize(320, 180)

        self._mpv: Any = None
        self._initialized = False
        self._last_position_ms = 0
        self._duration_ms = 0
        self._last_emitted_position_ms = -1
        self._eof_emitted = False
        self._pending_load: str | None = None
        self._autoplay_after_load = False

        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(_POLL_MS)
        self._poll_timer.timeout.connect(self._poll)

    def _ensure_mpv(self) -> Any:
        if self._mpv is None:
            _ensure_libmpv_findable()
            import mpv  # lazy: only loads libmpv-2.dll when the panel is first used
            self._mpv = mpv.MPV(
                wid=str(int(self.winId())),
                keep_open=True,
                pause=True,
                input_default_bindings=False,
                input_vo_keyboard=False,
                osc=False,
            )
        return self._mpv

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        if not self._initialized:
            # Defer mpv creation until after Windows has fully realized the
            # native window. Creating libmpv inside showEvent or with a 0ms
            # delay segfaults — the renderer can't bind until the window has
            # been mapped on screen, which takes a few frames on Windows.
            self._initialized = True
            QTimer.singleShot(200, self._finish_initialization)

    def _finish_initialization(self) -> None:
        self._ensure_mpv()
        self._poll_timer.start()
        if self._pending_load is not None:
            pending, self._pending_load = self._pending_load, None
            self.load(pending)
            if self._autoplay_after_load:
                self.play()
                self._autoplay_after_load = False

    def closeEvent(self, event: QCloseEvent) -> None:
        self.terminate()
        super().closeEvent(event)

    def terminate(self) -> None:
        """Release libmpv resources. Called automatically in closeEvent."""
        self._poll_timer.stop()
        if self._mpv is not None:
            try:
                self._mpv.terminate()
            except Exception:
                pass
            self._mpv = None

    def load(self, path: str | Path) -> None:
        if self._mpv is None:
            self._pending_load = str(path)
            return
        self._mpv.pause = True
        self._mpv.play(str(path))
        self._eof_emitted = False
        self._last_position_ms = 0
        self._last_emitted_position_ms = -1

    def play(self) -> None:
        if self._mpv is None:
            self._autoplay_after_load = True
            return
        self._mpv.pause = False

    def pause(self) -> None:
        if self._mpv is None:
            self._autoplay_after_load = False
            return
        self._mpv.pause = True

    def is_paused(self) -> bool:
        if self._mpv is None:
            return True
        try:
            return bool(self._mpv.pause)
        except Exception:
            return True

    def seek(self, ms: int) -> None:
        if self._mpv is None:
            return
        try:
            self._mpv.seek(ms / 1000.0, "absolute", "exact")
        except Exception:
            pass

    def position_ms(self) -> int:
        return self._last_position_ms

    def duration_ms(self) -> int:
        return self._duration_ms

    def _poll(self) -> None:
        if self._mpv is None:
            return

        try:
            pos = self._mpv.time_pos
            if pos is not None:
                self._last_position_ms = int(pos * 1000)
        except Exception:
            pass

        try:
            dur = self._mpv.duration
            if dur is not None and dur > 0:
                new_dur = int(dur * 1000)
                if new_dur != self._duration_ms:
                    self._duration_ms = new_dur
                    self.loaded.emit(self._duration_ms)
        except Exception:
            pass

        if self._last_position_ms != self._last_emitted_position_ms:
            self._last_emitted_position_ms = self._last_position_ms
            self.position_changed.emit(self._last_position_ms)

        try:
            eof = self._mpv.eof_reached
            if eof and not self._eof_emitted:
                self._eof_emitted = True
                self.ended.emit()
            elif not eof:
                self._eof_emitted = False
        except Exception:
            pass
