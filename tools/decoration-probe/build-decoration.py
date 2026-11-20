#!/usr/bin/env python3
# © Mayanktaker Computers & Web Development | https://mayanktaker.com
# SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development
# SPDX-License-Identifier: LGPL-2.0-or-later
"""Generate the Aurorae decoration and button SVGs for every variant.

The decoration is nine FrameSvg slices whose sizes, group offsets and gradient
coordinates are all derived from one padding value. Hand-editing them drifted
twice (a mask ate the corner shadow, then a strip double-composited over the
radial ramp), so the geometry now lives in PARAMS and the SVG is generated.
The five buttons share that geometry across variants: only their palette tones
differ, so a light-header variant cannot inherit night-toned glyphs.

Usage:
    build-decoration.py [--variant NAME] [--all] [--check] [path/to/decoration.svg]

--check regenerates every variant in memory and fails if the committed artwork
differs, so CI or a pre-commit hook can catch an out-of-band edit. Without it,
the selected variant's decoration and five buttons are written; --all writes
all five variants.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from buttons import build_buttons
DEFAULT_OUT = HERE.parent.parent / "themes" / "aurorae" / "MTNightshift" / "decoration.svg"

PARAMS = {
    # Shadow ring in px. KWin reserves this around the window and caches it for
    # the life of the compositor, so changing it shifts every client by the
    # difference until the session restarts. MTNightshiftrc's Padding* must
    # match it exactly.
    "padding": 32,
    # Distance at which the shadow has faded to nothing. Kept equal to the
    # padding: a shorter falloff leaves dead ring, and shrinking the padding is
    # what needs a compositor restart. Tune the weight with "peak" instead.
    "visible": 32,
    # Window corner arc. The client is inset "border" px on each side, so its
    # square corner sits (radius - border) * sqrt2 from the arc centre. That
    # distance must stay INSIDE the arc, or the client paints over the corner
    # band and the frame line disappears at the bottom corners — Aurorae does
    # not clip the client to the rounded shape, it only clips it to the window
    # silhouette. Guarded below.
    "radius": 10,      # matches kControlRadius: a window is never rounder than its contents
    "border": 6,           # must equal BorderLeft/Right/Bottom in MTNightshiftrc
    "header": 39,          # title bar height at 1x
    "centre": 64,          # FrameSvg centre slice
    # Cast-shadow alpha at the contour, and the shape of the falloff as
    # (fraction of the visible span, fraction of the peak). One ramp for every
    # direction, so edges and corners cannot disagree.
    "peak": 0.26,
    "envelope": [
        (0.0000, 1.000), (0.0781, 0.828), (0.1406, 0.643), (0.2031, 0.479),
        (0.2813, 0.346), (0.3750, 0.245), (0.5000, 0.143), (0.6563, 0.070),
        (0.8125, 0.021), (1.0000, 0.000),
    ],
    # Each variant's frame_line is an explicit token in VARIANTS: the window's
    # own outer line gets a stronger mix than the derived interior seams,
    # because Breeze derives its client hairline from the brighter Header
    # background: at equal contrast the client seam wins, and the outer edge
    # should be the dominant line. The shipped tokens sit at this mix from
    # Header to ForegroundNormal, except Nord Day one step stronger (#D8DCE4):
    # its narrow header/foreground span put the arc at the light-surface
    # coverage floor. They are frozen per variant so a header retune cannot
    # silently move the shipped edge. Keeping the outer edge a whisper above
    # the client seam (which follows [KDE] frameContrast=0.05, shipped by the
    # Global Theme) instead of a visible border is the 2026-11 polish pass.
    "frame_line_contrast": 0.06,
    # Disabled button glyphs step this fraction of the way from their header to
    # ForegroundInactive. One ratio for every variant, so the dimming reads the
    # same on a dark and a light titlebar. Disabled controls are exempt from the
    # text-contrast floor; the intent is "present but clearly out of action".
    "deactivated_mix": 0.65,
    # Thickness of the 1px frame line on the corner arcs. A 1px annulus spreads
    # over two pixels at ~50% coverage where the curve runs at 45 degrees, so the
    # corners read as a broken border against the crisp straight edges. The arcs
    # are drawn heavier to compensate; the straight edges stay exactly 1px.
    # Calibrated at "arc_calibration_radius"; a tighter arc crosses more pixels at
    # partial coverage over the same quarter turn, so the thickness is scaled by
    # calibration_radius / radius to hold the silhouette equally solid.
    "frame_line_arc": 2.0,
    "arc_calibration_radius": 15,
}

# Palette variants: geometry is shared, only the baked surface tones differ.
# header_* / window / foreground come from the matching color-schemes file's
# Header, Window and Window-text roles; foreground_inactive, negative and the
# selection pair come from its Header and Selection groups. frame_line is an
# explicit per-variant token: the blend(header_active, foreground,
# frame_line_contrast) result, one step stronger on Nord Day where the light
# header needs it. It is frozen per variant so a header retune cannot silently
# move the shipped edge.
VARIANTS = {
    "nightshift": {
        "title": "MT Nightshift",
        "out": HERE.parent.parent / "themes" / "aurorae" / "MTNightshift" / "decoration.svg",
        "palette": {
            "header_active": "#15181C",
            "header_inactive": "#101216",
            "window": "#101216",
            "foreground": "#E8EBF0",
            "foreground_inactive": "#8D97A4",
            "negative": "#D08084",
            "selection": "#1F6E9C",
            "selection_text": "#FFFFFF",
            "frame_line": "#222529",
        },
    },
    "dayshift": {
        "title": "MT Dayshift",
        "out": HERE.parent.parent / "themes" / "aurorae" / "MTDayshift" / "decoration.svg",
        "palette": {
            "header_active": "#F3F5F8",
            "header_inactive": "#EFF1F5",
            "window": "#EFF1F5",
            "foreground": "#1B1E22",
            "foreground_inactive": "#606873",
            "negative": "#AB484D",
            "selection": "#1F6E9C",
            "selection_text": "#FFFFFF",
            "frame_line": "#E6E8EB",
        },
    },
    "nord-night": {
        "title": "MT Nord Night",
        "out": HERE.parent.parent / "themes" / "aurorae" / "MTNordNight" / "decoration.svg",
        "palette": {
            "header_active": "#3B4252",
            "header_inactive": "#2E3440",
            "window": "#2E3440",
            "foreground": "#ECEFF4",
            "foreground_inactive": "#D8DEE9",
            "negative": "#F3B2B8",
            "selection": "#84A5C6",
            "selection_text": "#2E3440",
            "frame_line": "#464C5C",
        },
    },
    "nord-day": {
        "title": "MT Nord Day",
        "out": HERE.parent.parent / "themes" / "aurorae" / "MTNordDay" / "decoration.svg",
        "palette": {
            "header_active": "#E5E9F0",
            "header_inactive": "#D8DEE9",
            "window": "#ECEFF4",
            "foreground": "#2E3440",
            "foreground_inactive": "#4C566A",
            "negative": "#963F4A",
            "selection": "#4C6B91",
            "selection_text": "#FFFFFF",
            "frame_line": "#D8DCE4",
        },
    },
    "one-dark-pro": {
        "title": "MT One Dark Pro",
        "out": HERE.parent.parent / "themes" / "aurorae" / "MTOneDarkPro" / "decoration.svg",
        "palette": {
            "header_active": "#282C34",
            "header_inactive": "#21252B",
            "window": "#282C34",
            "foreground": "#D7DAE0",
            "foreground_inactive": "#B2B8C4",
            "negative": "#F4A1A9",
            "selection": "#528BFF",
            "selection_text": "#1D1F23",
            "frame_line": "#32363E",
        },
    },
}

P = R = H = C = 0
W_FRAME = H_FRAME = 0
ARC_THICKNESS = 0.0

# Starved by refresh_geometry(), never a literal: a dict built at import keeps the
# default footprint, so --radius/--padding would move the shadow square while the
# slice rects stayed put and left a dead band at the outer edge.
LAYOUT: dict[str, tuple[int, int, int, int]] = {}


def refresh_geometry() -> None:
    """Re-derives the module globals from PARAMS after an override.

    These used to be captured at import, which made every documented override
    (--padding, --radius, --peak, --arc) silently produce identical output.
    """
    global P, R, H, C, W_FRAME, H_FRAME, ARC_THICKNESS, LAYOUT
    P = PARAMS["padding"]
    R = PARAMS["radius"]
    H = PARAMS["header"]
    C = PARAMS["centre"]
    W_FRAME = 2 * (P + R) + C
    H_FRAME = (P + H) + C + (P + R)
    if PARAMS.get("arc_is_absolute"):
        ARC_THICKNESS = PARAMS["frame_line_arc"]
    else:
        ARC_THICKNESS = PARAMS["frame_line_arc"] * PARAMS["arc_calibration_radius"] / R
    LAYOUT.clear()
    LAYOUT.update({
        "topleft": (0, 0, P + R, P + H),
        "top": (P + R, 0, C, P + H),
        "topright": (W_FRAME - (P + R), 0, P + R, P + H),
        "left": (0, P + H, P + R, C),
        "center": (P + R, P + H, C, C),
        "right": (W_FRAME - (P + R), P + H, P + R, C),
        "bottomleft": (0, H_FRAME - (P + R), P + R, P + R),
        "bottom": (P + R, H_FRAME - (P + R), C, P + R),
        "bottomright": (W_FRAME - (P + R), H_FRAME - (P + R), P + R, P + R),
    })
    validate_geometry()


def validate_geometry() -> None:
    """Rejects a padding/radius pair that would bury the corner band.

    Runs on every refresh, not just at import: an override must not be able to
    produce artwork the committed files would never be allowed to hold.
    """
    if PARAMS["visible"] > P:
        raise SystemExit("visible falloff (%d) cannot exceed the padding ring (%d)"
                         % (PARAMS["visible"], P))
    # The corner band only shows if the client's square corner stays inside the arc.
    # Its distance along the diagonal is (R - border) * sqrt2; the band's inner edge
    # is R - frame_line_arc. Keeping 1px of air stops the client covering the band.
    client_corner = (R - PARAMS["border"]) * math.sqrt(2.0)
    band_inner = R - PARAMS["frame_line_arc"]
    slack = band_inner - client_corner
    if slack < 0.2:
        limit = int((PARAMS["border"] * math.sqrt(2.0) - PARAMS["frame_line_arc"] - 0.2)
                    / (math.sqrt(2.0) - 1.0))
        raise SystemExit(
            "radius %d is too large for border %d: the client's square corner reaches r=%.1f "
            "and the frame-line band starts at r=%.1f (slack %.2f), so the client covers the "
            "corner border. Keep radius <= %d." % (R, PARAMS["border"], client_corner,
                                                   band_inner, slack, limit))


refresh_geometry()


def blend(base: str, over: str, amount: float) -> str:
    """Mix two #RRGGBB colours; amount 0 keeps base, 1 returns over."""
    low = [int(base[i:i + 2], 16) for i in (1, 3, 5)]
    high = [int(over[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(round(a + (b - a) * amount) for a, b in zip(low, high))


# The frame line comes from the selected variant's explicit frame_line token;
# build() reads it from the palette it is handed, never from PARAMS at import.

def stops() -> str:
    """Linear-ramp stops, outer end first: offset 0 is furthest out, offset 1 is the contour."""
    rows = []
    for distance, shape in sorted(PARAMS["envelope"], reverse=True):
        rows.append(
            '      <stop offset="%.5f" stop-color="#000000" stop-opacity="%.3f"/>'
            % (1.0 - distance * PARAMS["visible"] / float(P), PARAMS["peak"] * shape)
        )
    return "\n".join(rows)


def radial_stops() -> str:
    """Corner-ramp stops: flat at the peak inside the arc, then the same falloff."""
    span = float(R + P)
    rows = [
        '      <stop offset="0" stop-color="#000000" stop-opacity="%.3f"/>' % PARAMS["peak"],
        '      <stop offset="%.5f" stop-color="#000000" stop-opacity="%.3f"/>'
        % (R / span, PARAMS["peak"]),
    ]
    for distance, shape in sorted(PARAMS["envelope"]):
        rows.append(
            '      <stop offset="%.5f" stop-color="#000000" stop-opacity="%.3f"/>'
            % ((R + distance * PARAMS["visible"]) / span, PARAMS["peak"] * shape)
        )
    return "\n".join(rows)


def gradients() -> str:
    """One ramp per direction plus one per corner."""
    edge, corner = stops(), radial_stops()
    span = R + P
    return f"""    <!-- Cast shadow ramps. Alpha envelope: {PARAMS["peak"]:.3f} at the contour, 0 at
         {PARAMS["visible"]}px. Every linear gradient runs outer end first, and the ring
         is {P}px so the falloff can be retuned without moving the frame geometry. -->
    <linearGradient id="shadow-top" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="{P}">
{edge}
    </linearGradient>
    <linearGradient id="shadow-bottom" gradientUnits="userSpaceOnUse" x1="0" y1="{span}" x2="0" y2="{R}">
{edge}
    </linearGradient>
    <linearGradient id="shadow-left" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{P}" y2="0">
{edge}
    </linearGradient>
    <linearGradient id="shadow-right" gradientUnits="userSpaceOnUse" x1="{span}" y1="0" x2="{R}" y2="0">
{edge}
    </linearGradient>
    <!-- Corner ramps are radial about the corner arc centre, so the shadow wraps
         the {R}px corner instead of stopping dead at the tangent points. -->
    <radialGradient id="shadow-topleft" gradientUnits="userSpaceOnUse" cx="{P + R}" cy="{P + R}" r="{span}">
{corner}
    </radialGradient>
    <radialGradient id="shadow-topright" gradientUnits="userSpaceOnUse" cx="0" cy="{P + R}" r="{span}">
{corner}
    </radialGradient>
    <radialGradient id="shadow-bottomleft" gradientUnits="userSpaceOnUse" cx="{P + R}" cy="0" r="{span}">
{corner}
    </radialGradient>
    <radialGradient id="shadow-bottomright" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="{span}">
{corner}
    </radialGradient>"""


# Window silhouette per corner, as (fill path, 1px frame-line path) in element space.
def shapes() -> dict[str, tuple[str, str]]:
    """Corner fill and frame-line paths.

    Built on demand for the same reason as LAYOUT: an f-string dict evaluated
    at import keeps the default radius, so --radius moved the slices but not
    the arcs drawn inside them.
    """
    return {
        "topleft": (
            f"M {P},{P + R} A {R},{R} 0 0 1 {P + R},{P} L {P + R},{P + H} L {P},{P + H} Z",
            f"M {P},{P + R} A {R},{R} 0 0 1 {P + R},{P} L {P + R},{P + 1} "
            f"A {R - 1},{R - 1} 0 0 0 {P + 1},{P + R} L {P + 1},{P + H} L {P},{P + H} Z",
        ),
        "topright": (
            f"M 0,{P} L 0,{P + H} L {R},{P + H} L {R},{P + R} A {R},{R} 0 0 0 0,{P} Z",
            f"M 0,{P} A {R},{R} 0 0 1 {R},{P + R} L {R},{P + H} L {R - 1},{P + H} "
            f"L {R - 1},{P + R} A {R - 1},{R - 1} 0 0 0 0,{P + 1} L 0,{P} Z",
        ),
        "bottomleft": (
            f"M {P},0 L {P + R},0 L {P + R},{R} A {R},{R} 0 0 1 {P},0 Z",
            f"M {P},0 A {R},{R} 0 0 0 {P + R},{R} L {P + R},{R - 1} "
            f"A {R - 1},{R - 1} 0 0 1 {P + 1},0 L {P},0 Z",
        ),
        "bottomright": (
            f"M 0,0 L {R},0 A {R},{R} 0 0 1 0,{R} L 0,0 Z",
            f"M {R},0 A {R},{R} 0 0 1 0,{R} L 0,{R - 1} "
            f"A {R - 1},{R - 1} 0 0 0 {R - 1},0 L {R},0 Z",
        ),
    }

# Slice geometry: (x, y, width, height) plus the shadow rects inside it.
# The top corners span the header, so they are taller than the bottom corners.

def shadow_rects(name: str) -> list[str]:
    """Shadow elements of one slice: a radial corner square, or an edge ramp.

    The radial rect stops at the corner square and the top corners add a linear
    strip beside the straight edge; they are adjacent, never overlapping, because
    two 0.28-alpha layers would composite to 0.48 and darken the tangent point.
    """
    if name in ("topleft", "topright"):
        x = 0 if name == "topleft" else R
        edge = "shadow-left" if name == "topleft" else "shadow-right"
        return [
            f'    <rect x="0" y="0" width="{P + R}" height="{P + R}" fill="url(#shadow-{name})"/>',
            f'    <rect x="{x}" y="{P + R}" width="{P}" height="{H - R}" fill="url(#{edge})"/>',
        ]
    if name in ("bottomleft", "bottomright"):
        return [f'    <rect x="0" y="0" width="{P + R}" height="{P + R}" fill="url(#shadow-{name})"/>']
    if name == "top":
        return [f'    <rect x="0" y="0" width="{C}" height="{P}" fill="url(#shadow-top)"/>']
    if name == "bottom":
        return [f'    <rect x="0" y="{R}" width="{C}" height="{P}" fill="url(#shadow-bottom)"/>']
    if name == "left":
        return [f'    <rect x="0" y="0" width="{P}" height="{C}" fill="url(#shadow-left)"/>']
    if name == "right":
        return [f'    <rect x="{R}" y="0" width="{P}" height="{C}" fill="url(#shadow-right)"/>']
    return []


def arc_stroke(name: str, frame: str) -> str:
    """Extra arc thickness for a corner: a stroke fully inside the silhouette.

    The 1px band already hugs the contour but antialiasing spreads it to ~50%
    coverage where the curve runs at 45 degrees, so the corner reads as a broken
    border. This adds the missing half-pixel. The sweep stops 6 degrees short of
    each tangent so the stroke's butt cap cannot poke into the shadow ring, where
    an opaque pixel would read as a double-shadow artefact.
    """
    extra = ARC_THICKNESS - 1.0
    if extra <= 0:
        return ""
    r = R - extra / 2.0
    # centre, start angle, end angle, sweep flag (degrees, y down)
    arcs = {
        "topleft": ((P + R, P + R), 186, 264, 1),
        "topright": ((0, P + R), 276, 354, 1),
        "bottomleft": ((P + R, 0), 174, 96, 0),
        "bottomright": ((0, 0), 6, 84, 1),
    }
    if name not in arcs:
        return ""
    (cx, cy), a0, a1, sweep = arcs[name]
    x0 = cx + r * math.cos(math.radians(a0))
    y0 = cy + r * math.sin(math.radians(a0))
    x1 = cx + r * math.cos(math.radians(a1))
    y1 = cy + r * math.sin(math.radians(a1))
    return (f'    <path d="M {x0:.2f},{y0:.2f} A {r:.2f},{r:.2f} 0 0 {sweep} {x1:.2f},{y1:.2f}" '
            f'fill="none" stroke="{frame}" stroke-width="{extra:.2f}"/>')


def surface(name: str, fill: str, frame: str) -> list[str]:
    """Window fill and 1px frame line of one slice."""
    width, height = LAYOUT[name][2], LAYOUT[name][3]
    if name in shapes():
        body, line = shapes()[name]
        rows = [f'    <path d="{body}" fill="{fill}"/>', f'    <path d="{line}" fill="{frame}"/>']
        extra = arc_stroke(name, frame)
        return rows + ([extra] if extra else [])
    if name == "top":
        return [f'    <rect x="0" y="{P}" width="{width}" height="{H}" fill="{fill}"/>',
                f'    <rect x="0" y="{P}" width="{width}" height="1" fill="{frame}"/>']
    if name == "bottom":
        return [f'    <rect x="0" y="0" width="{width}" height="{R}" fill="{fill}"/>',
                f'    <rect x="0" y="{R - 1}" width="{width}" height="1" fill="{frame}"/>']
    if name == "left":
        return [f'    <rect x="{P}" y="0" width="{R}" height="{height}" fill="{fill}"/>',
                f'    <rect x="{P}" y="0" width="1" height="{height}" fill="{frame}"/>']
    if name == "right":
        return [f'    <rect x="0" y="0" width="{R}" height="{height}" fill="{fill}"/>',
                f'    <rect x="{R - 1}" y="0" width="1" height="{height}" fill="{frame}"/>']
    return [f'    <rect x="0" y="0" width="{width}" height="{height}" fill="{fill}"/>']


def group(element_id: str, name: str, fill: str, frame: str, shadow: bool) -> str:
    """One FrameSvg slice group."""
    x, y, width, height = LAYOUT[name]
    rows = [f'  <g id="{element_id}" transform="translate({x},{y})">',
            f'    <rect x="0" y="0" width="{width}" height="{height}" fill="none" stroke="none"/>']
    rows += shadow_rects(name) if shadow else []
    rows += surface(name, fill, frame)
    rows.append("  </g>")
    return "\n".join(rows)


def masks() -> str:
    """Blur-region masks: the opaque window surface, no shadow."""
    rows = []
    for name in ("topleft", "topright", "bottomleft", "bottomright"):
        x, y, width, height = LAYOUT[name]
        rows.append(f'  <g id="mask-{name}" transform="translate({x},{y})">')
        rows.append(f'    <rect x="0" y="0" width="{width}" height="{height}" fill="none" stroke="none"/>')
        rows.append(f'    <path d="{shapes()[name][0]}" fill="#FFFFFF"/>')
        rows.append("  </g>")
    for name in ("top", "left", "right", "bottom", "center"):
        x, y, width, height = LAYOUT[name]
        rows.append(f'  <g id="mask-{name}" transform="translate({x},{y})">')
        rows.append(f'    <rect x="0" y="0" width="{width}" height="{height}" fill="none" stroke="none"/>')
        if name == "top":
            rows.append(f'    <rect x="0" y="{P}" width="{width}" height="{H}" fill="#FFFFFF"/>')
        elif name == "bottom":
            rows.append(f'    <rect x="0" y="0" width="{width}" height="{R}" fill="#FFFFFF"/>')
        elif name == "left":
            rows.append(f'    <rect x="{P}" y="0" width="{R}" height="{height}" fill="#FFFFFF"/>')
        elif name == "right":
            rows.append(f'    <rect x="0" y="0" width="{R}" height="{height}" fill="#FFFFFF"/>')
        else:
            rows.append(f'    <rect x="0" y="0" width="{width}" height="{height}" fill="#FFFFFF"/>')
        rows.append("  </g>")
    return "\n".join(rows)


def build(palette: dict[str, str], title: str) -> str:
    """Assemble the whole decoration document for one variant palette."""
    frame = palette["frame_line"]
    slices = [group(f"decoration-{n}", n, palette["header_active"], frame, True)
              for n in ("topleft", "top", "topright", "left", "center", "right",
                        "bottomleft", "bottom", "bottomright")]
    inactive = [group(f"decoration-inactive-{n}", n, palette["header_inactive"], frame, True)
                for n in ("topleft", "top", "topright", "left", "center", "right",
                          "bottomleft", "bottom", "bottomright")]
    maximized = [
        f'''  <g id="decoration-maximized-center" transform="translate(0,0)">
    <rect x="0" y="0" width="{C}" height="{C}" fill="none" stroke="none"/>
    <rect x="0" y="0" width="{C}" height="{C}" fill="{palette["header_active"]}"/>
  </g>''',
        f'''  <g id="decoration-maximized-inactive-center" transform="translate(0,0)">
    <rect x="0" y="0" width="{C}" height="{C}" fill="none" stroke="none"/>
    <rect x="0" y="0" width="{C}" height="{C}" fill="{palette["header_inactive"]}"/>
  </g>''',
    ]
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!--
  {title} Aurorae window decoration.
  © {2026} Mayanktaker Computers & Web Development | https://mayanktaker.com
  SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development
  SPDX-License-Identifier: LGPL-2.0-or-later

  GENERATED FILE — edit tools/decoration-probe/build-decoration.py instead.
  Regenerate with: tools/decoration-probe/build-decoration.py
  Verify with:     tools/decoration-probe/check-decoration.py

  Sculpted carbon frame: {R}px corners, 1px frame edge at the variant's
  explicit {frame} (chosen at blend(Header, foreground,
  {PARAMS["frame_line_contrast"]:.2f}) or one step stronger), opaque Header/Window fills, and a
  {"%.2f peak cast shadow fading to zero at %dpx inside a %dpx ring" % (PARAMS["peak"], PARAMS["visible"], P) if PARAMS["visible"] < P else "%.2f peak cast shadow filling the %dpx ring" % (PARAMS["peak"], P)}.
  Slice sizes: left/right {P + R}px, top {P + H}px, bottom {P + R}px, centre {C}x{C}.
  The {R}px radius lives in the corner tiles; corner ids must be FrameSvg's names
  (topleft, topright, bottomleft, bottomright) because FrameSvgHelpers::
  borderToElementId() looks them up.
  The cast shadow is gradient based: linear ramps on the edges and a radial ramp
  around each corner, so it wraps the silhouette instead of stopping at the
  corner tangent points.
-->
<svg xmlns="http://www.w3.org/2000/svg" width="{W_FRAME}" height="{H_FRAME}" viewBox="0 0 {W_FRAME} {H_FRAME}" version="1.1">
  <title>{title} window decoration</title>
  <desc>Active, inactive and maximized Aurorae decoration slices; {R}px corners; {P}px shadow padding.</desc>

  <defs>
{gradients()}
  </defs>

  <!-- Active decoration -->
{chr(10).join(slices)}

  <!-- Inactive decoration -->
{chr(10).join(inactive)}

  <!-- Maximized header strips (no corners or shadow) -->
{chr(10).join(maximized)}

  <!-- Blur masks: the opaque window surface, without shadow -->
{masks()}
</svg>
"""


def expected_artwork(name: str) -> dict[Path, str]:
    """Every generated file for one variant, as {path: document}."""
    spec = VARIANTS[name]
    documents = {spec["out"]: build(spec["palette"], spec["title"])}
    for button, document in build_buttons(spec["palette"], spec["title"], blend, PARAMS["deactivated_mix"]).items():
        documents[spec["out"].parent / (button + ".svg")] = document
    return documents


def main() -> int:
    """Write the artwork, or compare it with the files on disk.

    Geometry and weight can be overridden for a one-off trial without editing
    PARAMS, e.g. `--padding 24 --radius 10 --peak 0.22`. Nothing is written
    unless the result is what you asked for, so a trial goes to a scratch path.
    """
    argv = sys.argv[1:]
    overrides = {"--padding": "padding", "--visible": "visible", "--peak": "peak",
                 "--radius": "radius", "--arc": "frame_line_arc"}
    variant = "nightshift"
    check = False
    write_all = False
    rest = []
    index = 0
    while index < len(argv):
        token = argv[index]
        if token in overrides:
            key = overrides[token]
            value = argv[index + 1]
            PARAMS[key] = float(value) if key in ("peak", "frame_line_arc") else int(value)
            if key == "frame_line_arc":
                # An explicit --arc is an absolute width; the curvature scaling below
                # is what fills the value in when nobody overrode it.
                PARAMS["arc_is_absolute"] = True
            index += 2
            continue
        if token == "--variant":
            variant = argv[index + 1]
            if variant not in VARIANTS:
                raise SystemExit("unknown variant %r (have: %s)" % (variant, ", ".join(VARIANTS)))
            index += 2
            continue
        if token == "--check":
            check = True
            index += 1
            continue
        if token == "--all":
            write_all = True
            index += 1
            continue
        rest.append(token)
        index += 1

    refresh_geometry()

    if rest:
        # A one-off trial path holds the decoration only; buttons stay untouched.
        if write_all:
            raise SystemExit("--all writes the registered packages; drop the path argument")
        target = Path(rest[0])
        document = build(VARIANTS[variant]["palette"], VARIANTS[variant]["title"])
        if check:
            current = target.read_text() if target.exists() else ""
            if current != document:
                print("%s is stale: run tools/decoration-probe/build-decoration.py" % target)
                return 1
            print("%s matches the generator" % target)
            return 0
        target.write_text(document)
        print("wrote %s (%d lines)" % (target, document.count("\n")))
        return 0

    if check:
        # Drift-check every variant's committed decoration and buttons.
        stale = [str(path)
                 for name in VARIANTS
                 for path, document in expected_artwork(name).items()
                 if (path.read_text() if path.exists() else "") != document]
        if stale:
            print("stale artwork: %s" % ", ".join(stale))
            return 1
        print("all %d variants' decoration and button artwork match the generator"
              % len(VARIANTS))
        return 0

    for name in (list(VARIANTS) if write_all else [variant]):
        documents = expected_artwork(name)
        for path, document in documents.items():
            path.write_text(document)
        print("wrote %s and %d buttons (%d files)"
              % (VARIANTS[name]["out"], len(documents) - 1, len(documents)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
