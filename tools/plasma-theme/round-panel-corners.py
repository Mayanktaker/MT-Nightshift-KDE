#!/usr/bin/env python3
# © Mayanktaker Computers & Web Development | https://mayanktaker.com
# SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
# SPDX-License-Identifier: LGPL-2.0-or-later
"""Enlarge the corner radius of a Plasma panel-background SVG.

The stock Breeze panel-background (and our derived copy) draws its frame with
6px corner arcs inside 6px borders — fine for edge-to-edge panels, too tight
for floating ones. This script regenerates the frame section (the 44px-wide
panel face at the left of the file) with a larger corner radius: borders grow
to R, the four corner pieces become R quarter-rounds with a 1px
ColorScheme-Frame outline arc inset inside, and the centre band shrinks
accordingly. The shadow band (x > 47) and all shadow slices are copied through
untouched.

Usage: round-panel-corners.py <in.svg> <out.svg> [radius]
"""

from __future__ import annotations

import gzip
import math
import re
import sys
from pathlib import Path

K = 0.5523  # bezier circle approximation for quarter arcs

FRAME_W = 44.0   # frame region width in the source file (x 0..44)
FRAME_H = 44.0   # frame region height in the source file (y 10..54)
SRC_BORDER = 10  # source top/bottom border (the 6px arcs sit inside it)


def fmt(v: float) -> str:
    """Format a coordinate without a trailing .0 (matches Inkscape style)."""
    return str(int(v)) if v == int(v) else f"{v:.7g}"


def face_path(x: float, y: float, r: float, corner: str) -> str:
    """Filled quarter-round face piece for one corner of the frame region."""
    if corner == "tl":
        return (f"M {fmt(x)},{fmt(y + r)} H {fmt(x + r)} V {fmt(y)} "
                f"C {fmt(x + r - r * K)},{fmt(y)} {fmt(x)},{fmt(y + r - r * K)} "
                f"{fmt(x)},{fmt(y + r)} Z")
    if corner == "tr":
        return (f"M {fmt(x)},{fmt(y)} V {fmt(y + r)} H {fmt(x + r)} "
                f"C {fmt(x + r)},{fmt(y + r - r * K)} "
                f"{fmt(x + r - r * K)},{fmt(y)} {fmt(x)},{fmt(y)} Z")
    if corner == "bl":
        return (f"M {fmt(x)},{fmt(y)} H {fmt(x + r)} V {fmt(y + r)} "
                f"C {fmt(x + r)},{fmt(y + r * K)} "
                f"{fmt(x + r - r * K)},{fmt(y + r)} {fmt(x)},{fmt(y + r)} Z")
    return (f"M {fmt(x + r)},{fmt(y)} H {fmt(x)} V {fmt(y + r)} "
            f"C {fmt(x)},{fmt(y + r - r * K)} "
            f"{fmt(x + r - r * K)},{fmt(y + r)} {fmt(x + r)},{fmt(y)} Z")


def outline_path(x: float, y: float, r: float, corner: str) -> str:
    """1px-inside outline band for one corner, as a sampled-point polygon.

    Line segments only: arc commands crash the older qsvg parser CI uses, and
    the sampled form is exactly how the stock Breeze outlines are built."""
    n = 12
    # band centre circle: inset 1px from the face contour
    rr = r - 1.0
    centres = {"tl": (x + r, y + r), "tr": (x + r, y + r),
               "bl": (x + r, y + r), "br": (x + r, y + r)}
    cx, cy = centres[corner]
    spans = {"tl": (180, 270), "tr": (270, 360), "bl": (90, 180), "br": (0, 90)}
    a0, a1 = spans[corner]

    def arc_pts(rad: float, start: float, end: float) -> list:
        return [(cx + rad * math.cos(math.radians(a)),
                 cy + rad * math.sin(math.radians(a)))
                for a in [start + (end - start) * i / n for i in range(n + 1)]]

    outer = arc_pts(rr, a0, a1)
    inner = arc_pts(rr - 1.0, a0, a1)
    pts = outer + list(reversed(inner))
    d = "M " + " L ".join(f"{fmt(px)},{fmt(py)}" for px, py in pts) + " Z"
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

    frame_top = radius            # frame region moves down as borders grow
    frame_h = FRAME_H             # total frame height stays 44
    inner_w = FRAME_W - 2 * radius
    inner_h = frame_h - 2 * radius
    inner_y = frame_top + radius

    # 1. hints: Plasma reads these as the frame borders
    svg = re.sub(r'(<rect[^>]*id="hint-top-margin"[^>]*y=")\d+(?=")',
                 rf'\g<1>{frame_top}', svg)
    svg = re.sub(r'(<rect[^>]*id="hint-bottom-margin"[^>]*y=")\d+(?=")',
                 rf'\g<1>{64 - radius - 4}', svg)
    svg = re.sub(r'(<rect[^>]*id="hint-left-margin"[^>]*x=")\d+(?=")',
                 rf'\g<1>{radius}', svg)
    svg = re.sub(r'(<rect[^>]*id="hint-right-margin"[^>]*x=")\d+(?=")',
                 rf'\g<1>{44 - radius}', svg)
    svg = re.sub(r'(<rect[^>]*id="hint-top-inset"[^>]*y=")\d+(?=")',
                 rf'\g<1>{frame_top}', svg)
    svg = re.sub(r'(<rect[^>]*id="hint-bottom-inset"[^>]*y=")\d+(?=")',
                 rf'\g<1>{64 - radius - 4}', svg)
    svg = re.sub(r'(<rect[^>]*id="hint-left-inset"[^>]*x=")\d+(?=")',
                 rf'\g<1>{radius}', svg)
    svg = re.sub(r'(<rect[^>]*id="hint-right-inset"[^>]*x=")\d+(?=")',
                 rf'\g<1>{44 - radius}', svg)

    # 2. regenerate the nine-slice groups (frame region x 0..44, y frame_top..
    #    frame_top + frame_h; borders = radius)
    def group(ident: str, tx: float, ty: float, content: str) -> str:
        return (f'  <g\n     id="{ident}"\n     transform="translate({fmt(tx)},{fmt(ty)})">\n'
                f'{content}  </g>\n')

    bg = 'style="fill:currentColor" class="ColorScheme-Background"'
    fr = 'class="ColorScheme-Frame" style="fill:currentColor"'

    strip_w = fmt(inner_w)
    center_h = fmt(inner_h)
    side_h = fmt(frame_h - 2 * radius)

    new_groups = ""
    # top edge strip + its 1px inner line
    new_groups += group("top", radius, frame_top,
                         f'    <rect id="rect4152" height="6" {bg} width="{strip_w}" x="0" y="0" />\n'
                         f'    <rect {fr} x="0" y="0" width="{strip_w}" height="1" />\n')
    # bottom edge strip + its 1px inner line
    new_groups += group("bottom", radius, 64 - radius - 6,
                        f'    <rect id="rect4148" height="6" {bg} width="{strip_w}" x="0" y="0" />\n'
                        f'    <rect {fr} x="0" y="5" width="{strip_w}" height="1" />\n')
    # left edge strip + its 1px inner line
    new_groups += group("left", 0, frame_top + radius,
                        f'    <rect id="rect4144" height="{side_h}" {bg} width="{fmt(radius)}" x="0" y="0" />\n'
                        f'    <rect {fr} x="0" y="0" width="1" height="{side_h}" />\n')
    # right edge strip + its 1px inner line
    new_groups += group("right", 44 - radius, frame_top + radius,
                        f'    <rect id="rect4140" height="{side_h}" {bg} width="{fmt(radius)}" x="0" y="0" />\n'
                        f'    <rect {fr} x="0" y="0" width="1" height="{side_h}" />\n')
    # centre
    new_groups += group("center", radius, frame_top + radius,
                        f'    <rect id="rect4138" height="{center_h}" {bg} width="{strip_w}" x="0" y="0" />\n')
    # four corners: face quarter-round + 1px inner outline arc
    corners = [("topleft", 0, frame_top, "tl"),
               ("topright", 44 - radius, frame_top, "tr"),
               ("bottomleft", 0, 64 - frame_top - radius, "bl"),
               ("bottomright", 44 - radius, 64 - frame_top - radius, "br")]
    for ident, cx, cy, p in corners:
        # paths are built in the group's LOCAL space (origin 0,0); the group
        # translate positions the piece.
        content = face_path(0, 0, radius, p) + outline_path(0, 0, radius, p)
        new_groups += group(ident, cx, cy, content)

    # 3. replace the frame section in the file: from the top group through the
    #    hint insets, keeping masks and shadow slices byte-identical.
    start = svg.index('<g\n     id="top"')
    mask_top = svg.index('<rect\n     id="mask-top"', start)
    svg = svg[:start] + new_groups + svg[mask_top:]

    payload = svg.encode()
    if out_gzip:
        import gzip as _gzip
        payload = _gzip.compress(payload, mtime=0)
    dst.write_bytes(payload)
    print(f"wrote {dst} with corner radius {radius}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
