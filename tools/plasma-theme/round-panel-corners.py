#!/usr/bin/env python3
# © Mayanktaker Computers & Web Development | https://mayanktaker.com
# SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
# SPDX-License-Identifier: LGPL-2.0-or-later
"""Enlarge the corner radius of a Plasma panel-background SVG.

The stock Breeze panel-background (and our derived copy) draws its frame with
6px corner arcs inside 6px borders — fine for edge-to-edge panels, too tight
for floating ones. This script regenerates the frame section (the 44px-wide
panel face at the left of the file) with a larger corner radius: the border
slices grow to R (KSvg derives border sizes from the slice elements' sizes),
the four corner pieces become R quarter-rounds with a 1px ColorScheme-Frame
band inside the contour, and the centre shrinks accordingly. The shadow band
(x > 47) and all shadow slices are copied through untouched, as are the margin
hints (their 4px size is the content margin; their positions stay inside the
wider bands).

Usage: round-panel-corners.py <in.svg|in.svgz> <out.svg|out.svgz> [radius]
"""

from __future__ import annotations

import gzip
import math
import sys
from pathlib import Path

K = 0.5523        # bezier circle approximation for quarter arcs
FRAME_W = 44.0    # frame region width in the source file (x 0..44)
FRAME_TOP = 10.0  # frame region top in the source file (y 10..54)
N_SAMPLE = 12     # sampled points per quarter arc


def fmt(v: float) -> str:
    """Format a coordinate without a trailing .0 (matches Inkscape style)."""
    return str(int(v)) if v == int(v) else f"{v:.7g}"


def arc_pts(cx: float, cy: float, rad: float, a0: float, a1: float) -> list:
    """Sampled points along a circle; angles in degrees, y-down SVG coords."""
    return [(cx + rad * math.cos(math.radians(a)), cy + rad * math.sin(math.radians(a)))
            for a in [a0 + (a1 - a0) * i / N_SAMPLE for i in range(N_SAMPLE + 1)]]


def poly_d(pts: list) -> str:
    return "M " + " L ".join(f"{fmt(px)},{fmt(py)}" for px, py in pts) + " Z"


def face_corner(corner: str, r: float) -> str:
    """Filled face piece (local 0..r square, outer corner cut by the arc).

    The face = square minus the quarter-disc centred at the piece's INNER
    corner; the transparent sliver sits at the OUTER corner and creates the
    rounded silhouette through the frame mask.
    """
    # inner corner = disc centre; outer arc from a0 to a1 (degrees, y-down)
    spec = {"tl": ((r, r), 180, 270), "tr": ((0, r), 270, 360),
            "bl": ((r, 0), 90, 180), "br": ((0, 0), 0, 90)}
    (cx, cy), a0, a1 = spec[corner]
    pts = arc_pts(cx, cy, r, a0, a1)
    # the two square edges beyond the arc endpoints, closing the polygon
    edges = {"tl": [(r, r)], "tr": [(r, 0)], "bl": [(0, r)], "br": [(0, 0)]}
    d = poly_d(pts + edges[corner])
    return (f'    <path d="{d}" style="fill:currentColor" '
            f'class="ColorScheme-Background" id="face-{corner}" />\n')


def outline_corner(corner: str, r: float) -> str:
    """1px-inside outline band for one corner, as a sampled filled polygon.

    The band follows the face contour arc (radius r) between the two strip
    line junctions, inset 1px along the straight edges, and returns along an
    arc of radius r-1. Line segments only: arc commands crash the older qsvg
    parser CI uses, and the sampled form matches the stock Breeze outlines.
    """
    spec = {"tl": ((r, r), 180, 270), "tr": ((0, r), 270, 360),
            "bl": ((r, 0), 90, 180), "br": ((0, 0), 0, 90)}
    (cx, cy), a0, a1 = spec[corner]
    # junctions: where the strip 1px lines meet the contour
    junction = {"tl": (r, 0), "tr": (0, 0), "bl": (0, 0), "br": (r, 0)}
    inset = {"tl": (1, r), "tr": (r - 1, r), "bl": (1, r - 1), "br": (r - 1, r - 1)}
    outer = arc_pts(cx, cy, r, a0, a1)
    inner = arc_pts(cx, cy, r - 1, a0, a1)
    d = poly_d([junction[corner]] + outer + [inset[corner]] + list(reversed(inner)))
    return (f'    <path d="{d}" style="fill:currentColor" '
            f'class="ColorScheme-Frame" id="outline-{corner}" />\n')


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    radius = float(sys.argv[3]) if len(sys.argv) > 3 else 14.0
    raw = src.read_bytes()
    # transparent gzip support: theme files ship as .svgz
    svg = (gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw).decode()
    out_gzip = dst.suffix == ".svgz"

    r = radius
    bw = fmt(r)             # border width (all four sides)
    mid_ty = fmt(FRAME_TOP + r)         # centre/left/right band y
    strip_w = fmt(44 - 2 * r)           # top/bottom strip width
    side_h = fmt(44 - 2 * r)            # left/right strip height
    bottom_line_y = fmt(r - 1)          # 1px line inside the bottom strip
    right_line_x = fmt(r - 1)           # 1px line inside the right strip

    bg = 'style="fill:currentColor" class="ColorScheme-Background"'
    fr = 'class="ColorScheme-Frame" style="fill:currentColor"'

    def group(ident: str, tx: float, ty: float, content: str) -> str:
        return (f'  <g\n     id="{ident}"\n     transform="translate({fmt(tx)},{fmt(ty)})">\n'
                f'{content}  </g>\n')

    new_groups = ""
    # top edge strip + its 1px line at the outer edge
    new_groups += group("top", r, FRAME_TOP,
                        f'    <rect id="rect4152" height="{bw}" {bg} width="{strip_w}" x="0" y="0" />\n'
                        f'    <rect {fr} x="0" y="0" width="{strip_w}" height="1" />\n')
    # bottom edge strip + its 1px line at the outer edge
    new_groups += group("bottom", r, 64 - r,
                        f'    <rect id="rect4148" height="{bw}" {bg} width="{strip_w}" x="0" y="0" />\n'
                        f'    <rect {fr} x="0" y="{bottom_line_y}" width="{strip_w}" height="1" />\n')
    # left edge strip + its 1px line at the outer edge
    new_groups += group("left", 0, FRAME_TOP + r,
                        f'    <rect id="rect4144" height="{side_h}" {bg} width="{bw}" x="0" y="0" />\n'
                        f'    <rect {fr} x="0" y="0" width="1" height="{side_h}" />\n')
    # right edge strip + its 1px line at the outer edge
    new_groups += group("right", 44 - r, FRAME_TOP + r,
                        f'    <rect id="rect4140" height="{side_h}" {bg} width="{bw}" x="0" y="0" />\n'
                        f'    <rect {fr} x="{right_line_x}" y="0" width="1" height="{side_h}" />\n')
    # centre
    new_groups += group("center", r, FRAME_TOP + r,
                        f'    <rect id="rect4138" height="{side_h}" {bg} width="{strip_w}" x="0" y="0" />\n')
    # four corners: face quarter-round + 1px outline band
    corners = [("topleft", 0, FRAME_TOP, "tl"),
               ("topright", 44 - r, FRAME_TOP, "tr"),
               ("bottomleft", 0, 64 - r, "bl"),
               ("bottomright", 44 - r, 64 - r, "br")]
    for ident, cx, cy, p in corners:
        # paths are built in the group's LOCAL space; translate positions it
        content = face_corner(p, r) + outline_corner(p, r)
        new_groups += group(ident, cx, cy, content)

    # margin hint rects: sizes are the content margins (4px), positions inside
    # the new, wider bands; KSvg reads only their sizes.
    def hint(ident: str, x: float, y: float, w: float, h: float) -> str:
        return (f'  <rect\n     id="{ident}"\n     y="{fmt(y)}"\n     x="{fmt(x)}"\n'
                f'     height="{fmt(h)}"\n     width="{fmt(w)}"\n'
                f'     style="fill:#ff6600" />\n')

    hints = (hint("hint-top-margin", 20, FRAME_TOP, 4, 4)
             + hint("hint-bottom-margin", 20, 64 - r - 4, 4, 4)
             + hint("hint-right-margin", 44 - r - 4, 30, 4, 4)
             + hint("hint-left-margin", r, 30, 4, 4)
             + hint("hint-top-inset", 20, FRAME_TOP, 4, 1e-9)
             + hint("hint-bottom-inset", 20, 64 - r - 4, 4, 1e-9)
             + hint("hint-right-inset", 44 - r - 4, 30, 1e-9, 4)
             + hint("hint-left-inset", r, 30, 1e-9, 4))

    # splice: replace everything from the top group to the mask rects; masks
    # and shadow slices are preserved byte-identical.
    start = svg.index('<g\n     id="top"')
    mask_top = svg.index('<rect\n     id="mask-top"', start)
    svg = svg[:start] + new_groups + hints + svg[mask_top:]

    payload = svg.encode()
    if out_gzip:
        payload = gzip.compress(payload, mtime=0)
    dst.write_bytes(payload)
    print(f"wrote {dst} with corner radius {radius}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
