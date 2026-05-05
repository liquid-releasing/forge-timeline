# forge-timeline — spec

This document is the design contract for `forge-timeline` v0. It is the
single source of truth for what the library does, what it does not do, and
how consumers compose it. Code in `src/forge_timeline/` should never go
beyond what this spec describes; if a feature is wanted that the spec does
not cover, this document gets revised first.

---

## Scope

In scope:

- Render a multi-staff time-series canvas synchronized to a media duration.
- Render a baton (vertical line) tracking a playhead position in
  milliseconds.
- Accept user interaction (click, drag, wheel-zoom, shift-wheel-pan,
  range-select) and emit signals consumers wire up.
- Render a libmpv-backed video preview synchronized to the same playhead.
- Provide a controller (`BatonSync`) that keeps the timeline baton and the
  video preview's playhead lock-stepped in both directions.

Out of scope:

- Audio analysis (lives in `videoflow`).
- Moment detection / scene-cut / beat detection (lives in `videoflow`).
- Funscript editing logic (lives in consumer apps).
- Sidecar IO (chapters.json, events.yml, fragments) — consumers own their
  domain objects; this library renders what they hand it.
- Cookbook / fragment library plumbing (lives in `videoflow.structural`).

---

## Public API surface

The package exports exactly three top-level primitives plus two helpers:

```python
from forge_timeline import TimelineWidget, VideoPanel, BatonSync
from forge_timeline import format_time, parse_time
```

Everything else (individual staves, baton widget, mini-map, theme) is
internal but importable for consumers who want to build a custom layout.

### `TimelineWidget`

```
TimelineWidget(QWidget)
    mode: Literal["canvas", "navigator"]
    duration_ms: int
    staves: list[Staff]
    set_position(ms: int) -> None
    set_zoom(factor: float, center_ms: int | None = None) -> None
    set_pan(start_ms: int) -> None
    set_data(chapters=..., phrases=..., curve=..., thumbnails=...) -> None

    Signals:
        position_clicked(ms: int)         # user clicked anywhere on a staff
        position_dragged(ms: int)         # user is scrubbing the baton
        range_selected(start_ms, end_ms)  # range drag on waveform
        zoom_changed(factor: float)
        pan_changed(start_ms: int)
```

Composition rules:

- `mode="navigator"` → only movement staff + baton; no thumbnails, no
  waveform, no curve, no mini-map.
- `mode="canvas"` → all staves the consumer asks for, in this top-to-bottom
  order: mini-map, waveform, movement, measure, note, thumbnail, baton
  overlay.
- Any staff is opt-in via the `staves` constructor arg or `add_staff()`.

### `VideoPanel`

```
VideoPanel(QWidget)
    load(path: str | Path) -> None
    play() -> None
    pause() -> None
    seek(ms: int) -> None
    position_ms() -> int
    duration_ms() -> int

    Signals:
        position_changed(ms: int)         # emitted at libmpv's update rate
        loaded(duration_ms: int)
        ended()
```

Implementation: thin libmpv wrapper. The Qt embedding strategy follows
forgeplayer's existing approach (libmpv-2.dll with a render context bound
to a `QOpenGLWidget`). On platforms where libmpv is unavailable, the
widget shows a placeholder and `load()` raises.

### `BatonSync`

```
BatonSync(timeline: TimelineWidget, video: VideoPanel)
    enabled: bool
```

Wires the bidirectional coupling:

- `video.position_changed` → `timeline.set_position`
- `timeline.position_clicked` / `position_dragged` → `video.seek`
- `range_selected` → `video.seek(start_ms)` + (optional) loop region

Disposable: `unsync()` detaches both directions.

### `format_time(ms: int) -> str` and `parse_time(text: str) -> int`

Pure helpers for the `HH:MM:SS.mmm` precision time format used everywhere
in the editor UIs. No Qt dependency.

---

## Render modes

| Aspect | `canvas` | `navigator` |
| --- | --- | --- |
| Editing | Yes | No (read-only) |
| Spoiler-safe | Configurable | Yes by default |
| Default for | forgegen, forgeassembler, FunscriptForge, beatflo | forgeplayer |
| Thumbnail strip | Default on | Off |
| Curve / measure detail | Yes | No |
| Mini-map | On | Off |

`navigator` is intentionally not "canvas with everything turned off." Its
contract is "show the user where they are in the movement, no more." That
keeps it cheap to render in forgeplayer's playback path.

---

## Track stack (canvas mode, top to bottom)

1. **Mini-map** — compressed full-file overview (~24 px tall). Viewport
   rectangle highlights the slice the main timeline currently shows.
   Click → main jumps. Drag rect → pans. Drag rect edges → zooms.
   Optional faint chapter ticks + mode-color heat overlay.
2. **Waveform** — Audacity-style audio rendering. Clickable; range-select
   loops playback over selection.
3. **Movement staff** — chapter bands (name, content_type chip, exclude
   state, build-state shading).
4. **Measure staff** — phrases nested inside movement bands; mode-color
   coded; intent label.
5. **Note staff** — funscript curve as sparkline; redraws on edit.
6. **Thumbnail strip** — video frames sampled at staff width;
   default-on in canvas mode, off in navigator.
7. **Baton** — vertical line spanning all staves; tracks playhead and the
   active edit zone.

Every staff is a `QWidget` subclass conforming to a `Staff` interface
(set_data, set_zoom, set_pan, paintEvent). Apps may add custom staves;
the TimelineWidget composition root does not assume the canonical set.

---

## Interaction contract

| Gesture | Effect |
| --- | --- |
| Click any staff at any X | Baton jumps; `position_clicked(ms)` |
| Drag baton | Scrub; `position_dragged(ms)` continuously |
| Wheel | Zoom centered on cursor (max 24 hours visible → 200 ms visible) |
| Shift-wheel | Pan |
| Arrow keys | Pan one viewport / 10 |
| Range-drag on waveform | `range_selected(start, end)`; consumer typically loops video over selection |
| Mini-map click | Main timeline jumps to that fraction of duration |
| Mini-map drag rect | Pans main timeline |
| Mini-map drag rect edge | Zooms main timeline |

Spinner is forbidden. Long-running consumer work surfaces as **baton sweep
+ progressive paint** of staves (grey → colored as data lands). The
TimelineWidget exposes per-staff `mark_pending(start_ms, end_ms)` and
`mark_built(start_ms, end_ms)` hooks for this pattern.

---

## Data shapes (what consumers hand the timeline)

These are inputs to `set_data()`. The library does not persist them and
does not own their schema; consumers' sidecars do.

```python
Chapter = TypedDict("Chapter", {
    "start_ms": int,
    "end_ms": int,
    "name": str,
    "content_type": str | None,        # "music" | "dialogue" | ...
    "excluded": bool,
    "build_state": Literal["pending", "in_progress", "built"],
})

Phrase = TypedDict("Phrase", {
    "start_ms": int,
    "end_ms": int,
    "intent": str,
    "mode": str | None,                # mode-recipe name; drives color
    "chapter_index": int | None,
})

Curve = list[tuple[int, int]]          # (at_ms, value 0-100)

Thumbnail = TypedDict("Thumbnail", {
    "at_ms": int,
    "image_path": str,                 # PNG/JPG on disk
})
```

Mismatched data (a phrase whose range crosses a chapter boundary, a
chapter past `duration_ms`, etc.) is rendered with a divergence indicator
but never silently dropped or coerced. Consumers handle the policy.

---

## Theming

`forge_timeline.theme` exposes design tokens (colors, fonts, sizes).
Consumers may override via the `Theme` constructor handed to
`TimelineWidget(..., theme=...)`. Default palette is dark — the forge
apps' visual baseline.

Mode-color mapping is consumer-supplied (the library does not know which
mode is "edge" vs "climax"); the consumer hands a `mode -> QColor` dict
on `set_data()`.

---

## Out-of-scope (deliberate)

These are explicitly NOT this library's job, even though they are nearby:

- **Detect chapter boundaries.** That is `videoflow.structural`. The
  library renders an interactive "accept/refine proposed boundary" UI
  in a future release, but the engine lives elsewhere.
- **Detect beats, scene cuts, or moments.** That is the moment detector
  in `videoflow`. Forge-timeline will gain a `proposals` overlay that
  renders candidate moments handed to it by a consumer; the analysis
  itself stays out.
- **Read or write sidecars.** Consumers load `chapters.json`,
  `phrases.json`, fragments, etc. and hand the library the in-memory
  shapes above.
- **Funscript edit operations.** A consumer (FunscriptForge, beatflo)
  owns the action-curve manipulation; the library renders the result.

---

## Versioning

`v0.x` — pre-alpha, breaking changes free-fire as the spec settles.
`v1.0` — locked when at least two consumer apps (one canvas mode, one
navigator mode) are using the library against real workloads.
