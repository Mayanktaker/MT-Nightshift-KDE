#!/usr/bin/env python3
# © Mayanktaker Computers & Web Development | https://mayanktaker.com
# SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development
# SPDX-License-Identifier: LGPL-2.0-or-later
"""Generate themes/aurorae/MTNightshift/decoration.svg from design parameters.

The decoration is nine FrameSvg slices whose sizes, group offsets and gradient
coordinates are all derived from one padding value. Hand-editing them drifted
twice (a mask ate the corner shadow, then a strip double-composited over the
radial ramp), so the geometry now lives in PARAMS and the SVG is generated.

Usage:
    build-decoration.py [--check] [path/to/decoration.svg]

--check regenerates in memory and fails if the file on disk differs, so CI or a
pre-commit hook can catch an out-of-band edit.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
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
    "radius": 21,          # window corner arc, independent of the padding
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
    # Palette, from color-schemes/MT-Nightshift.colors.
    "header_active": "#15181C",
    "header_inactive": "#101216",
    "window": "#101216",
    "foreground": "#E8EBF0",
    # Interior seams follow [KDE] frameContrast (0.14, shipped by the Global
    # Theme). The window's own outer line gets a stronger mix, because Breeze
    # derives its client hairline from the brighter Header background: at equal
    # contrast the client seam wins, and the outer edge should be the dominant
    # line. 0.20 puts the frame at #3F4246 against the client's #33363A.
    "frame_contrast": 0.14,
    "frame_line_contrast": 0.20,
}

P = PARAMS["padding"]
R = PARAMS["radius"]
H = PARAMS["header"]
C = PARAMS["centre"]
W_FRAME = 2 * (P + R) + C
H_FRAME = (P + H) + C + (P + R)

if PARAMS["visible"] > P:
    raise SystemExit("visible falloff (%d) cannot exceed the padding ring (%d)"
                     % (PARAMS["visible"], P))


def blend(base: str, over: str, amount: float) -> str:
    """Mix two #RRGGBB colours; amount 0 keeps base, 1 returns over."""
    low = [int(base[i:i + 2], 16) for i in (1, 3, 5)]
    high = [int(over[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(round(a + (b - a) * amount) for a, b in zip(low, high))


# The frame line colour is derived, not literals, so a palette retune follows.
PARAMS["frame"] = blend(PARAMS["header_active"], PARAMS["foreground"],
                        PARAMS["frame_line_contrast"])

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
SHAPES = {
    "topleft": (
        f"M {P},{P + R} A {R},{R} 0 0 1 {P + R},{P} L {P + R},{P + H} L {P},{P + H} Z",
        f"M {P},{P + R} A {R},{R} 0 0 1 {P + R},{P} L {P + R},{P + 1} "
        f"A {R - 1},{R - 1} 0 0 0 {P + 1},{P + R} L {P + 1},{P + H} L {P},{P + H} Z",
    ),
    "topright": (
        f"M 0,{P} L 0,{P + H} L {R},{P + H} L {R},{P + R} A {R},{R} 0 0 0 0,{P} Z",
        f"M 0,{P} A {R},{R} 0 0 1 {R},{P + R} L {R},{P + H} L {R - 1},{P + H} "
        f"L {R - 1},{P + R} A {R - 1},{R - 1} 0 0 0 1,{P} L 0,{P} Z",
    ),
    "bottomleft": (
        f"M {P},0 L {P + R},0 L {P + R},{R} A {R},{R} 0 0 1 {P},0 Z",
        f"M {P},0 A {R},{R} 0 0 0 {P + R},{R} L {P + R - 1},{R} "
        f"A {R - 1},{R - 1} 0 0 1 {P + 1},0 L {P},0 Z",
    ),
    "bottomright": (
        f"M 0,0 L {R},0 A {R},{R} 0 0 1 0,{R} L 0,0 Z",
        f"M {R},0 A {R},{R} 0 0 1 0,{R} L 1,{R} A {R - 1},{R - 1} 0 0 0 {R - 1},0 L {R},0 Z",
    ),
}

# Slice geometry: (x, y, width, height) plus the shadow rects inside it.
# The top corners span the header, so they are taller than the bottom corners.
LAYOUT = {
    "topleft": (0, 0, P + R, P + H),
    "top": (P + R, 0, C, P + H),
    "topright": (W_FRAME - (P + R), 0, P + R, P + H),
    "left": (0, P + H, P + R, C),
    "center": (P + R, P + H, C, C),
    "right": (W_FRAME - (P + R), P + H, P + R, C),
    "bottomleft": (0, H_FRAME - (P + R), P + R, P + R),
    "bottom": (P + R, H_FRAME - (P + R), C, P + R),
    "bottomright": (W_FRAME - (P + R), H_FRAME - (P + R), P + R, P + R),
}


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


def surface(name: str, fill: str) -> list[str]:
    """Window fill and 1px frame line of one slice."""
    width, height = LAYOUT[name][2], LAYOUT[name][3]
    if name in SHAPES:
        body, line = SHAPES[name]
        return [f'    <path d="{body}" fill="{fill}"/>', f'    <path d="{line}" fill="{PARAMS["frame"]}"/>']
    if name == "top":
        return [f'    <rect x="0" y="{P}" width="{width}" height="{H}" fill="{fill}"/>',
                f'    <rect x="0" y="{P}" width="{width}" height="1" fill="{PARAMS["frame"]}"/>']
    if name == "bottom":
        return [f'    <rect x="0" y="0" width="{width}" height="{R}" fill="{fill}"/>',
                f'    <rect x="0" y="{R - 1}" width="{width}" height="1" fill="{PARAMS["frame"]}"/>']
    if name == "left":
        return [f'    <rect x="{P}" y="0" width="{R}" height="{height}" fill="{fill}"/>',
                f'    <rect x="{P}" y="0" width="1" height="{height}" fill="{PARAMS["frame"]}"/>']
    if name == "right":
        return [f'    <rect x="0" y="0" width="{R}" height="{height}" fill="{fill}"/>',
                f'    <rect x="{R - 1}" y="0" width="1" height="{height}" fill="{PARAMS["frame"]}"/>']
    return [f'    <rect x="0" y="0" width="{width}" height="{height}" fill="{fill}"/>']


def group(element_id: str, name: str, fill: str, shadow: bool) -> str:
    """One FrameSvg slice group."""
    x, y, width, height = LAYOUT[name]
    rows = [f'  <g id="{element_id}" transform="translate({x},{y})">',
            f'    <rect x="0" y="0" width="{width}" height="{height}" fill="none" stroke="none"/>']
    rows += shadow_rects(name) if shadow else []
    rows += surface(name, fill)
    rows.append("  </g>")
    return "\n".join(rows)


def masks() -> str:
    """Blur-region masks: the opaque window surface, no shadow."""
    rows = []
    for name in ("topleft", "topright", "bottomleft", "bottomright"):
        x, y, width, height = LAYOUT[name]
        rows.append(f'  <g id="mask-{name}" transform="translate({x},{y})">')
        rows.append(f'    <rect x="0" y="0" width="{width}" height="{height}" fill="none" stroke="none"/>')
        rows.append(f'    <path d="{SHAPES[name][0]}" fill="#FFFFFF"/>')
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


def build() -> str:
    """Assemble the whole document."""
    slices = [group(f"decoration-{n}", n, PARAMS["header_active"], True)
              for n in ("topleft", "top", "topright", "left", "center", "right",
                        "bottomleft", "bottom", "bottomright")]
    inactive = [group(f"decoration-inactive-{n}", n, PARAMS["header_inactive"], True)
                for n in ("topleft", "top", "topright", "left", "center", "right",
                          "bottomleft", "bottom", "bottomright")]
    maximized = [
        f'''  <g id="decoration-maximized-center" transform="translate(0,0)">
    <rect x="0" y="0" width="{C}" height="{C}" fill="none" stroke="none"/>
    <rect x="0" y="0" width="{C}" height="{C}" fill="{PARAMS["header_active"]}"/>
  </g>''',
        f'''  <g id="decoration-maximized-inactive-center" transform="translate(0,0)">
    <rect x="0" y="0" width="{C}" height="{C}" fill="none" stroke="none"/>
    <rect x="0" y="0" width="{C}" height="{C}" fill="{PARAMS["header_inactive"]}"/>
  </g>''',
    ]
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!--
  MT Nightshift Aurorae window decoration.
  © {2026} Mayanktaker Computers & Web Development | https://mayanktaker.com
  SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development
  SPDX-License-Identifier: LGPL-2.0-or-later

  GENERATED FILE — edit tools/decoration-probe/build-decoration.py instead.
  Regenerate with: tools/decoration-probe/build-decoration.py
  Verify with:     tools/decoration-probe/check-decoration.py

  Sculpted carbon frame: {R}px corners, 1px frame edge at
  blend(Header, foreground, {PARAMS["frame_line_contrast"]:.2f}), opaque Header/Window fills, and a
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
  <title>MT Nightshift window decoration</title>
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


def main() -> int:
    """Write the SVG, or compare it with the file on disk."""
    args = [a for a in sys.argv[1:] if a != "--check"]
    target = Path(args[0]) if args else DEFAULT_OUT
    document = build()
    if "--check" in sys.argv:
        current = target.read_text() if target.exists() else ""
        if current != document:
            print("decoration.svg is stale: run tools/decoration-probe/build-decoration.py")
            return 1
        print("decoration.svg matches the generator")
        return 0
    target.write_text(document)
    print("wrote %s (%d lines)" % (target, document.count("\n")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
