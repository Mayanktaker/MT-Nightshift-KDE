# MT Nightshift — window decoration

© Mayanktaker Computers & Web Development | https://mayanktaker.com

The Aurorae window decoration is a separate package from the Plasma Style, so its
specification lives here rather than in [`design.md`](design.md). `design.md` links
to this file from §12 and keeps the shape rules that are shared with the rest of
the suite (§6) and the palette (§2).

Generated, never hand-edited: every `decoration.svg` and the five button SVGs come
from `tools/decoration-probe/build-decoration.py`; see [`validation.md`](validation.md)
for what the probe measures and what it cannot see.

## Overview

`themes/aurorae/MTNightshift/` is the **Sculpted** window edge: a user-local Aurorae decoration for the same palette. It is deliberately separate from the Plasma Style: it does not change the 6px panel/dialog radius in `design.md` §6, and installing one does not install the other. The 10px corner is the **window** corner only.

## 1. Geometry

- **The corner band is reinforced, never widened.** A 1px annulus spreads across two pixels at partial coverage where the arc runs at 45 degrees, so the corners read as a broken border against the crisp straight edges. The fix is a **second 1px coverage pass along the same annulus** (`frame_line_arc = 2.0` → a 1px stroke on the same [R−1, R] band): the partial alpha compounds and the corner reaches full strength without the line getting thicker. It must stay inside the band. Widening the stroke instead — which the first attempt did, 2.0px at radius 10 — draws a 2px line that steps down to 1px at the tangent point, and that step is plainly visible. Both are asserted: `stroke-width <= 1px` structurally, and the measured band width in pixels.
- **10px outer corners**, drawn as a true quarter-circle in the four corner tiles, with a 1px `ColorScheme-Frame` line inside the contour. Fills are opaque; there is no gradient or inner highlight. 10px is `kControlRadius`: the window is the same roundness as every button, field, hover pill and tooltip it contains.
- **Title bar 39px at 1x**: 7px above, a 24px title/button row, 8px below. The caption is centred between the button groups and uses KWin's title font; the SVG contains no text or fonts.
- **Buttons 24×24**, 8px apart, 10px from the frame edge. KWin builds both groups from its own settings (`ButtonsOnLeft` defaults to `MSE`, `ButtonsOnRight` to `HIAX`); the theme only supplies the artwork, and a button without an SVG is dropped from the group. Shipped: `minimize`, `maximize`, `restore`, `close`, and `menu` for the window-menu button. The `LeftButtons`/`RightButtons` keys in `MTNightshiftrc` are v1 keys and are not read by Aurorae v2.
- **Shadow ring 32px, ramp across the whole ring**, drawn as four gradient ramps rather than stacked flat-alpha slices: one linear ramp per edge and one radial ramp per corner, all on the same envelope — 0.26 alpha at the contour, 0 at 32px. The original ramp was 0.384 and read as a heavy dark halo on a bright wallpaper; 0.26 over the full ring keeps separation, softens the falloff and leaves no dead ring, since the reserved `padding` is what KWin caches for the life of the compositor (shrinking it shifts every client by the difference until the session restarts). `visible` can be set shorter than `padding` to concentrate the shadow if that trade is ever wanted. The corner ramps are radial about the corner arc centre, so the cast shadow wraps the 10px silhouette instead of stopping at the tangent points; the shadow meets the straight edges continuously and is never painted inside the window rectangle. Because the ramps are radial, no corner cutout mask is needed or shipped. A slice-based shadow (nested flat rects) re-creates visible alpha stairs on its 2–5px bands, which is why the ramps are gradients.
- **The border must run round the corners.** Each corner's frame line is an annulus between the silhouette arc (`r` = 10) and a *concentric* arc at `r` = 9; both must share the corner centre, or the band becomes a lune that thins to ~0.4px at the 45° point and reads as a missing border on a light wallpaper. Two further causes were measured: a 1px annulus only reaches ~50% coverage per pixel where the curve runs diagonally, so each arc gets a second 1px coverage pass on the same annulus (stopped 6° short of each tangent so the cap cannot leak into the shadow ring) while the straight edges keep their single pass; and with a 6px border the client's square corner sits at (10 − 6)·√2 = 5.66 from the arc centre, so it must fall inside the band's inner edge or the client paints the corner border away — which is what kept the bottom corners empty. Measured live before: top-left 0.85 mean, the other three 0.35 with 0.00 at the diagonal, and 0.00 under the client; after: all four 0.95 mean / 0.78 minimum.
- **17px is the ceiling.** `build-decoration.py` re-runs its padding/radius guard on every override. The drawn band is 1px, so the client's square corner — at `(R − border)·√2` along the diagonal — must stay inside `R − 1`. With the default 6px border that holds up to **17** (`--radius 18` is rejected: the client corner reaches r=17.0 against a band starting at r=17.0). An earlier version of the guard subtracted the *stroke width* from the band and reported 15, which is 2px conservative. Going past 17 needs `BorderSize=VeryLarge`, which thickens every window frame in the session — a user preference, not a theme property. The shipped 10px sits far inside that limit.
- **Corner language: 10px, Normal border.** The earlier 21px corner needed `BorderSize=VeryLarge` (border 8) to clear the client's corner, and that thickens every window frame in the session — a user preference, not a theme property. At the default border the legal range is 1–17px; 10px is chosen to match the controls, and `build-decoration.py` refuses any radius/border pair that would bury the frame line again.
- **HiDPI: the reinforcement is a 1x compensation.** At 2x the rasteriser has four times the pixels across the same band, so a bare 1px arc is already solid; the second pass exists only to beat 1x antialiasing. `make check-dpr2` renders `--arc 1.0` — no reinforcement at all — at 2x and fails if the corner border develops a gap, so the compensation is proven to be unnecessary there rather than assumed.
- **Where the radial stops.** Each top corner element also spans 18px of straight window edge below the arc, and a radial ramp under-darkens that strip, so the top corner elements carry a linear `shadow-left`/`shadow-right` strip there and the radial rect is clipped to the 45×45 corner square — the two must not overlap, or the alpha composites (two 0.26 layers composite to 0.45 and the tangent point turns into a dark blob). The bottom corner elements need no strip: their arc is tangent to the window's left edge at the element's own top row, so the whole element is corner territory. Adding one there painted a darker band into the bottom corners and stepped the shadow where the side element ends.
- **Checks:** `tools/decoration-probe/check-decoration.py` rasterises every slice through Qt's qsvg plugin, re-stitches the frame and asserts the invariants that have broken before (ramped edges, shadow in the corner cutouts, no alpha above the envelope, no divider row, expected fills). Run it after any change to this file.
- **No title divider.** Breeze paints the toolbar area of a Qt Widgets window with the `Header` palette group and closes it with a 1px frame line derived from `[KDE] frameContrast` — measured as `blend(Header, ForegroundNormal, frameContrast)` = `#202327` at the theme's 0.05. That line sits 7px below the 39px boundary, so a divider in the SVG put a second, darker seam (`#0A0B0D`) 8px above the real edge and split one continuous header-toned surface in two. The SVG therefore ends the header flush at 39px and leaves the single separator to the client. Windows whose client area is not header-toned still separate by the `Header` `#15181C` → `Window` `#101216` tone step, which is how Breeze itself separates them.
- **Maximized**: a 32px flat header (4px + 24px + 4px), no corners, no shadow.

## 2. Palette

| Element | Colour |
| --- | --- |
| Active header | `#15181C` (`Header` background) |
| Inactive header | `#101216` (`Header[Inactive]` background) |
| Frame sides and bottom | the variant's header tone (active / inactive), not `Window` — Nightshift `#15181C` / `#101216`, Dayshift `#F3F5F8` / `#EFF1F5`, Nord Night `#3B4252` / `#2E3440`, Nord Day `#E5E9F0` / `#D8DEE9` |
| Frame line | `#222529`, an explicit per-variant `frame_line`; Nightshift's value is `blend(Header, ForegroundNormal, 0.06)`, deliberately stronger than the derived interior seams so the outer edge stays dominant (§8) |
| Active title | `#E8EBF0` |
| Inactive title | `#C8CED6` |
| Active button icon | `#E8EBF0` (`ForegroundNormal`) |
| Hover icon and outline | `#D08084` (`ForegroundNegative`), no fill |
| Pressed fill / glyph | `#1F6E9C` (`Selection` background) / `#FFFFFF` (`Selection` text) |
| Inactive button icon | `#8D97A4` (`ForegroundInactive`) |
| Disabled button icon | `blend(header, ForegroundInactive, 0.65)` |
| Hover outline, inactive window | `#8D97A4` (`ForegroundInactive`, 6.3:1 on the inactive header) |

The table above names Nightshift's tones; the matrix below covers every baked
role for all five variants. Those tones are baked per variant by
`tools/decoration-probe/build-decoration.py` from the `VARIANTS` palette table:

| Element | Nightshift | Dayshift | Nord Night | Nord Day | One Dark Pro |
| --- | --- | --- | --- | --- | --- |
| Active / inactive header (and frame sides) | `#15181C` / `#101216` | `#F3F5F8` / `#EFF1F5` | `#3B4252` / `#2E3440` | `#E5E9F0` / `#D8DEE9` | `#282C34` / `#21252B` |
| Frame line | `#222529` | `#E6E8EB` | `#464C5C` | `#D8DCE4` | `#32363E` |
| Active glyph | `#E8EBF0` | `#1B1E22` | `#ECEFF4` | `#2E3440` | `#D7DAE0` |
| Inactive glyph | `#8D97A4` | `#606873` | `#D8DEE9` | `#4C566A` | `#B2B8C4` |
| Hover glyph + outline | `#D08084` | `#AB484D` | `#F3B2B8` | `#963F4A` | `#F4A1A9` |
| Pressed fill / glyph | `#1F6E9C` / `#FFFFFF` | `#1F6E9C` / `#FFFFFF` | `#84A5C6` / `#2E3440` | `#4C6B91` / `#FFFFFF` | `#528BFF` / `#1D1F23` |
| Hover-inactive ring / glyph | `#8D97A4` | `#606873` | `#D8DEE9` | `#4C566A` | `#B2B8C4` |
| Disabled glyph | `blend(header, ForegroundInactive, 0.65)` of that variant, all five |

Measured contrast for the generated buttons (`check-buttons.py`), all above the
3:1 non-text and 4.5:1 text floors:

| Variant | Active | Inactive | Hover | Pressed text | Hover-inactive ring |
| --- | --- | --- | --- | --- | --- |
| Nightshift | 14.90 | 6.02 | 6.02 | 5.57 | 6.33 |
| Dayshift | 15.32 | 5.16 | 5.11 | 5.57 | 4.99 |
| Nord Night | 8.73 | 7.45 | 5.69 | 4.86 | 9.25 |
| Nord Day | 10.26 | 6.06 | 5.55 | 5.50 | 5.46 |
| One Dark Pro | 10.00 | 7.73 | 7.01 | 5.10 | 7.73 |

The five decorations and their five button sets each share paths, rects and stroke widths and differ only in colour; `check-buttons.py` fingerprints that geometry so the promise holds. Each palette carries `header_active`, `header_inactive`, `window`, `foreground`, `foreground_inactive`, `negative`, `selection`, `selection_text` and an explicit `frame_line`. Nord Day's frame line is `#D8DCE4`, one step above the 0.06 mix, because its header-to-foreground span is the narrowest of the five and the 0.06 value left the corner arcs at the light-surface coverage floor. Button tones follow the variant scheme rather than a baked set: Nord Night's selection pill is light `#84A5C6`, so its pressed glyph is dark `#2E3440` where Nightshift, Dayshift and Nord Day use `#FFFFFF` (One Dark Pro uses `#1D1F23`).

## 3. States

- **Rest**: no button background, icon only, in the variant's `ForegroundNormal`.
- **Hover**: 1px outline with a 6px rounded-square radius, no fill; the outline and icon take the variant's `ForegroundNegative`.
- **Pressed**: a filled 6px rounded-square disc in the variant's selection background, with the selection text tone as the glyph, and no outline.
- **Disabled**: a dimmed glyph, no disc, stepped 65% from the header toward `ForegroundInactive`.
- **Inactive window**: buttons drop to `ForegroundInactive`; hover-inactive keeps that glyph under a `ForegroundInactive` ring, which clears the 3:1 non-text floor on the inactive header (Nightshift 6.3:1, Dayshift 5.0:1, Nord Night 9.3:1, Nord Day 5.5:1); pressed-inactive uses the selection fill with selection text.
- State changes never move or resize a control. The negative tone is a transient hover cue only, never a resting colour.

## 4. HiDPI and Aurorae constraints

- Geometry is vector. KWin renders the SVG at the window's device pixel ratio, so the 1px frame line and 1.5–1.6px glyph strokes stay at 1 and 1.5–1.6 logical pixels at 2x.
- Aurorae clamps `BorderLeft`/`BorderRight`/`BorderBottom` to KWin's **BorderSize** setting. At the default Normal size the frame is `6/6/6`; the 10px arc then stays clear of the client's square corner with 3.3px of air (the 45-degree client corner sits at r=5.66, the 1px band starts at r=9). Tiny/NoSides (1–4px) can show a small notch at the bottom corners because the client is inset less than the arc; the shadow still carries the silhouette. `None` hides the bottom arc entirely.
- Aurorae v2 derives the window shadow from the decoration's padding ring and cuts it at the window rectangle. The `mask-*` elements are supplied for the blur region; v2 uses them for blur only, and blur is disabled in this theme.
- **Two knobs tune the shell geometry**, both in `PARAMS`: `peak` (cast-shadow weight) and `frame_line_arc` (arc reinforcement weight: `2.0` means a second 1px pass, never a wider line). `frame_line_contrast` stays in `PARAMS` only as the recorded derivation (`blend(Header, ForegroundNormal, 0.06)`, printed in the generated SVG comment); it no longer computes a colour. Since Task 2 the outer line is each variant's explicit `frame_line` token from §2, and every slice — left/right sides and bottom included — is filled with the variant's header tone, not `Window`. `build-decoration.py` takes `--padding/--visible/--peak/--arc` overrides for a one-off trial, and `make check` / `make apply` wrap the verify and install sequences.
- **Corner tiles must be named `topleft`, `topright`, `bottomleft`, `bottomright`.** `FrameSvg` resolves the corners through `FrameSvgHelpers::borderToElementId()`, so a tile named `tl`/`br` is never requested: the corner stays transparent, the header and side fills lose their ends, and the shadow splits into four detached bars. FrameSvg also scales each corner element to its section rect, which is `leftMargin × topMargin` for the top corners and `leftMargin × bottomMargin` for the bottom ones; keep the element sizes at `45×63` and `45×45` (padding + radius, or padding + header for the top corners) — `tools/decoration-probe/build-decoration.py` derives them from one padding value. Check a change with a real `FrameSvg` render, not a plain SVG preview.
- **The window-menu button needs `menu.svg`.** `ButtonsOnLeft` defaults to `MSE`, and v2 instantiates the menu button even when the theme has no artwork: without `menu.svg` it falls back to `FallbackMenuDecorationButton`, which paints the full-colour window icon (a blue Dolphin icon on a dark titlebar). `menu.svg` carries the same eight state prefixes as the other buttons and the same three-rule glyph in the variant's `ForegroundNormal`.
- **Button paths are resolved once per KWin process.** `DecorationTheme` keeps every resolved path in a `Q_GLOBAL_STATIC` list and `onDecorationSettingsChanged()` only reparses `auroraerc`; adding or renaming a button SVG therefore has no effect until KWin restarts — `reconfigure`, a new window, or switching the theme away and back all reuse the cached object, so a fresh window shows new `decoration.svg` pixels but keeps the old button paths. Validate a new button file only after a KWin restart. The v1 QML engine (`org.kde.kwin.aurorae`) has no `menu.svg` lookup at all: its `MenuButton.qml` always paints the window icon, so the themed glyph appears only under `org.kde.kwin.aurorae.v2`.
- `decoration-maximized` and `decoration-maximized-inactive` are top strips; KWin clips decoration painting to the title border. Maximize and restore use separate `maximize.svg` and `restore.svg` files, each carrying all eight button-state prefixes.
- The title/button row is tuned for the default title font and `ButtonSize` (100%). KWin grows the titlebar when the button-size factor grows, but the SVG header slice is fixed at 39px; the extra height is painted with the `Window` centre colour and the header boundary stays at 39px. Keep the default size for the intended single-tone header.
- Shadow is not drawn when the window is maximized; Aurorae v2 sets a null shadow and the maximized header is flat.
- `metadata.desktop` (with `Type=Service`, `Name` and `X-KDE-PluginInfo-Name=MTNightshift`) is the package entry. Aurorae themes are plain directory themes, not KPackage bundles, so `kpackagetool6` does not apply.

The Aurorae artwork is original and licensed LGPL-2.0-or-later. No upstream Breeze file is copied or modified by this package. The derived Plasma Style omits a blanket package license because its upstream assets carry multiple file-level licenses; preserve each file's original notices.
