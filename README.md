# forge-timeline

PySide6 timeline-canvas widget library for the lqr forge apps —
[forgegen](https://github.com/liquid-releasing/forgegen),
[forgeplayer](https://github.com/liquid-releasing/forgeplayer),
[forgeassembler](https://github.com/liquid-releasing/forgeassembler),
[FunscriptForge](https://github.com/liquid-releasing/funscriptforge), and
[beatflo](https://github.com/liquid-releasing/beatflo).

One timeline canvas, two render modes, three coordinated primitives —
`TimelineWidget`, `VideoPanel`, `BatonSync`. Every editor and player in the
forge family composes these into its own grid layout.

## Status

Pre-alpha. Skeleton + spec only — no rendering implemented yet. The design
contract lives in [docs/spec.md](docs/spec.md).

## Why this exists

The forge apps were each cutting their own timeline. forgeplayer had a
chapter-nav strip; forgegen had a progress spinner; forgeassembler had button
grids; FunscriptForge had no spatial context at all. Users couldn't see where
they were in the score. Worse, every app was solving the same canvas
problem differently.

`forge-timeline` is the canvas they all share. Two render modes:

- **`canvas`** — full editing surface (forgegen, forgeassembler, beatflo,
  FunscriptForge): waveform, movement staff, measure staff, note staff,
  thumbnail strip, mini-map, and a baton.
- **`navigator`** — read-only, spoiler-safe (forgeplayer): movement staff
  only, no thumbnails, no measure detail.

## The three primitives

| Widget | Role |
| --- | --- |
| `TimelineWidget` | The layered staves. Click any staff at any X → baton jumps. Wheel zooms; shift-wheel pans. Range-select on the waveform loops playback. |
| `VideoPanel` | libmpv-backed video preview. Plays the section under the baton. |
| `BatonSync` | Controller that keeps the timeline baton and the video playhead in lock-step in both directions. |

Apps compose these with their own `QGridLayout` / `QSplitter` plus
app-specific controls (detector params, phrase palette, assembly track).

## Vocabulary

User-facing UI uses the orchestra metaphor:

| User sees | Code uses |
| --- | --- |
| **Movement** | chapter |
| **Measure** | phrase |
| **Note** | action / stroke |
| **Staff** | track |
| **Baton** | playhead |

This package's public API uses the code-side names. App user guides translate.

## Install

```bash
pip install -e ".[mpv,dev]"
```

`PySide6` is a hard dep. `python-mpv` is optional (only needed for
`VideoPanel`). `pytest-qt` is for the test suite.

### libmpv-2.dll — required for VideoPanel only

`VideoPanel` lazily imports `mpv` and loads `libmpv-2.dll` on first
`showEvent`. The rest of the package (`TimelineWidget`,
`PrecisionTimeLabel`, etc.) imports cleanly without it.

On Windows, drop `libmpv-2.dll` next to the venv's `python.exe` — i.e.
`.venv/Scripts/libmpv-2.dll`. `VideoPanel` adds that directory to the
DLL search on first use, so direct-execution `python.exe` works
identically to a `venv\Scripts\activate` shell. The forgeplayer repo
includes a working copy:

```bash
copy ..\forgeplayer\libmpv-2.dll .venv\Scripts\
```

## Examples

```bash
python examples/navigator_minimal.py    # forgeplayer-shape demo (no video)
python examples/canvas_full.py           # FunscriptForge / beatflo-shape (no video)
python examples/video_demo.py            # full stack — video panel + timeline + time label
```

## Repo layout

```
forge-timeline/
├── docs/spec.md
├── src/forge_timeline/
│   ├── timeline.py          TimelineWidget composition root
│   ├── video_panel.py       libmpv-backed video preview
│   ├── baton_sync.py        timeline ↔ video sync controller
│   ├── time_format.py       HH:MM:SS.mmm formatting (implemented)
│   ├── baton.py             baton widget
│   ├── minimap.py           full-file overview strip
│   ├── theme.py             design tokens
│   └── staves/
│       ├── waveform.py
│       ├── movement.py
│       ├── measure.py
│       ├── note.py
│       └── thumbnail.py
├── examples/
└── tests/
```

## License

MIT — see [LICENSE](LICENSE).
