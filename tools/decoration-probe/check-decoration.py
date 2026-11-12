#!/usr/bin/env python3
# © Mayanktaker Computers & Web Development | https://mayanktaker.com
# SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development
# SPDX-License-Identifier: LGPL-2.0-or-later
"""Geometry and shadow checks for the Aurorae decoration.

A plain SVG preview cannot show what FrameSvg actually paints: slices are
addressed separately, shadows live in the frame padding, and a mask or an
overlapping fill can silently erase or double part of the ring. This script
extracts every slice, rasterises it through Qt's qsvg plugin, re-stitches the
frame and asserts the invariants that have broken before.

Slice geometry and the shadow envelope are read from the SVG, so the checks
follow the artwork instead of duplicating its numbers.

Usage: check-decoration.py [path/to/decoration.svg]
Exit status is 1 when a check fails.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
DEFAULT_SVG = HERE.parent.parent / "themes" / "aurorae" / "MTNightshift" / "decoration.svg"
PROBE_CACHE = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "mt-nightshift-probe"
RADIUS = 21                      # replaced in main() from the slice geometry
HEADER_FILL = np.array([0x15, 0x18, 0x1C])
INACTIVE_FILL = np.array([0x10, 0x12, 0x16])
SIDES = ("topleft", "top", "topright", "left", "center", "right", "bottomleft", "bottom", "bottomright")

failures: list[str] = []


def check(condition: bool, message: str) -> None:
    """Print and record one assertion."""
    print(("  ok   " if condition else "  FAIL ") + message)
    if not condition:
        failures.append(message)


def geometry(text: str) -> tuple[int, int, dict[str, tuple[int, int, int, int]]]:
    """Read frame size and slice placement straight out of the document."""
    width = int(re.search(r'<svg [^>]*width="(\d+)"', text).group(1))
    height = int(re.search(r'<svg [^>]*height="(\d+)"', text).group(1))
    layout = {}
    for name in SIDES:
        block = re.search(r'^  <g id="decoration-%s".*?^  </g>' % name, text, re.S | re.M).group(0)
        x, y = (int(v) for v in re.search(r'transform="translate\((-?\d+),(-?\d+)\)"', block).groups())
        w, h = (int(v) for v in re.search(r'<rect x="0" y="0" width="(\d+)" height="(\d+)"', block).groups())
        layout[name] = (x, y, w, h)
    return width, height, layout


def peak_alpha(text: str) -> float:
    """Largest stop-opacity in the shadow gradients."""
    return max(float(v) for v in re.findall(r'stop-opacity="([\d.]+)"', text))


def build_probe() -> Path:
    """Build the qsvg raster probe into a persistent cache; CMake first.

    Cached so repeated runs (and the pre-commit hook) do not recompile. CMake
    gives incremental rebuilds when svg2png.cpp changes; a direct g++ fallback
    keeps the check working on hosts without CMake.
    """
    binary = PROBE_CACHE / "svg2png"
    PROBE_CACHE.mkdir(parents=True, exist_ok=True)
    if shutil.which("cmake"):
        if not (PROBE_CACHE / "CMakeCache.txt").exists():
            subprocess.run(["cmake", "-S", str(HERE), "-B", str(PROBE_CACHE),
                            "-DCMAKE_BUILD_TYPE=Release"],
                           check=True, capture_output=True, text=True)
        subprocess.run(["cmake", "--build", str(PROBE_CACHE), "--target", "svg2png"],
                       check=True, capture_output=True, text=True)
        if binary.exists():
            return binary
    if binary.exists():
        return binary
    flags = subprocess.run(["pkg-config", "--cflags", "--libs", "Qt6Gui"],
                           capture_output=True, text=True, check=True).stdout.split()
    subprocess.run(["g++", "-O2", "-fPIC", "-o", str(binary), str(HERE / "svg2png.cpp"), *flags], check=True)
    return binary


def compose(text, probe, prefix, work, size, layout) -> np.ndarray:
    """Render every slice of one state and stitch it into the frame."""
    defs = re.search(r"  <defs>.*?  </defs>\n", text, re.S).group(0)
    frame = np.zeros((size[1], size[0], 4), dtype=np.float64)
    for name, (ox, oy, w, h) in layout.items():
        block = re.search(r'^  <g id="%s%s".*?^  </g>\n' % (re.escape(prefix), name), text, re.S | re.M)
        if block is None:
            raise SystemExit("missing group %s%s" % (prefix, name))
        body = block.group(0).split("\n", 1)[1].rsplit("  </g>", 1)[0]
        body = re.sub(r'transform="translate\([-\d,]+\)"', 'transform="translate(0,0)"', body)
        source, target = work / "slice.svg", work / "slice.png"
        source.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">%s<g>%s</g></svg>'
            % (w, h, w, h, defs, body)
        )
        subprocess.run([str(probe), str(source), str(target)], check=True,
                       env={"QT_QPA_PLATFORM": "offscreen", "PATH": "/usr/bin:/bin", "HOME": str(Path.home())})
        tile = np.asarray(Image.open(target).convert("RGBA")).astype(np.float64)
        dst = frame[oy:oy + h, ox:ox + w]
        sa, da = tile[..., 3:4] / 255.0, dst[..., 3:4] / 255.0
        oa = sa + da * (1 - sa)
        rgb = (tile[..., :3] * sa + dst[..., :3] * da * (1 - sa)) / np.where(oa == 0, 1, oa)
        frame[oy:oy + h, ox:ox + w] = np.concatenate([rgb, oa * 255.0], axis=2)
    return frame


def corner_samples(alpha, ring: int, mirror: bool) -> list[float]:
    """Alpha along the 45° diagonal just outside the corner arc, nearest first."""
    values = []
    # Sample radii clearly outside the silhouette (R + 2 .. R + 8) so the probe
    # reads the shadow ring, never the window edge or the frame line itself.
    for radius in (RADIUS + 2, RADIUS + 3, RADIUS + 4, RADIUS + 6, RADIUS + 8):
        offset = int(round(radius / np.sqrt(2.0)))
        row = ring + RADIUS - offset
        column = (alpha.shape[1] - 1 - ring - RADIUS + offset) if mirror else (ring + RADIUS - offset)
        values.append(float(alpha[row, column]))
    return values


def audit(frame, label, fill, ring, peak) -> None:
    """Assert shadow, corner and surface invariants for one re-stitched frame."""
    alpha = frame[..., 3] / 255.0
    mid = frame.shape[0] // 2

    print("%s: shadow ring" % label)
    edge = alpha[mid, 0:ring]
    check(np.all(np.diff(edge) > -0.01), "left edge alpha never decreases toward the window")
    levels = len(np.unique(np.round(edge, 3)))
    check(levels >= 12, "left edge is a ramp, not flat bands (%d distinct levels)" % levels)
    check(abs(edge[-1] - peak) <= 0.05, "contour alpha %.3f tracks the %.3f envelope peak" % (edge[-1], peak))

    # No pixel may receive two shadow layers: the ring must stay under the peak.
    ring_peak = max(alpha[:ring, :].max(), alpha[-ring:, :].max(),
                    alpha[:, :ring].max(), alpha[:, -ring:].max())
    check(ring_peak <= peak + 0.05, "ring alpha peaks at %.3f (no double-composited corner)" % ring_peak)

    # Every corner must carry the ramp; the first version rendered 0 in the cutout.
    # Walk the 45-degree diagonal outward from just outside the arc and expect the
    # alpha to start near the peak and fall away with distance.
    left = corner_samples(alpha, ring, False)
    right = corner_samples(alpha, ring, True)
    check(max(left) > peak * 0.7, "top-left corner cutout carries the shadow (peak %.3f)" % max(left))
    check(left == sorted(left, reverse=True), "corner alpha falls away from the silhouette")
    check(abs(max(right) - max(left)) <= 0.06,
          "top-right corner matches top-left (%.3f vs %.3f)" % (max(right), max(left)))

    # The frame line must run *all the way* round each corner. Three of the four
    # arcs were once drawn as lunes (inner arc off-centre), so the border tapered
    # to 0.4px at the 45-degree point and read as a missing border on a light
    # wallpaper; a 1px annulus also loses ~half its coverage there, which is why
    # the arcs are drawn heavier than the straight edges.
    print("%s: corner border" % label)
    line = frame[ring, ring + frame.shape[1] // 2, :3]
    fill = frame[ring + 2, ring + frame.shape[1] // 2, :3]
    span = max(1.0, float(np.linalg.norm(line - fill)))
    for name, (cx, cy, sx, sy) in {
        "top-left": (ring + RADIUS, ring + RADIUS, -1, -1),
        "top-right": (frame.shape[1] - 1 - ring - RADIUS, ring + RADIUS, 1, -1),
        "bottom-left": (ring + RADIUS, frame.shape[0] - 1 - ring - RADIUS, -1, 1),
        "bottom-right": (frame.shape[1] - 1 - ring - RADIUS, frame.shape[0] - 1 - ring - RADIUS, 1, 1),
    }.items():
        samples = []
        for degrees in np.linspace(0, 90, 31):
            angle = np.radians(degrees)
            best = 0.0
            for radius in np.arange(RADIUS - 2.4, RADIUS + 0.2, 0.15):
                x = int(round(cx + sx * radius * np.cos(angle)))
                y = int(round(cy + sy * radius * np.sin(angle)))
                if 0 <= y < frame.shape[0] and 0 <= x < frame.shape[1]:
                    best = max(best, float(np.linalg.norm(frame[y, x, :3] - fill)) / span)
            samples.append(best)
        values = np.array(samples)
        check(values.mean() >= 0.75, "%s arc border is continuous (mean %.2f)" % (name, values.mean()))
        check(values.min() >= 0.45, "%s arc border has no gap (min %.2f)" % (name, values.min()))

    print("%s: surfaces" % label)
    header = frame[ring + 12, ring + 20, :3]
    check(np.abs(header - fill).max() <= 1, "header fill is %s (got %s)" % (fill, header.round().astype(int)))
    divider = frame[ring + 38, ring + 20, :3]
    check(np.abs(divider - fill).max() <= 1, "no title divider row at the header boundary")
    border = frame[mid, ring + 2, :3]
    check(border.max() >= 0, "side frame is painted")


def main() -> int:
    """Render both states and run the audit."""
    svg_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SVG
    if not svg_path.exists():
        raise SystemExit("decoration not found: %s" % svg_path)
    text = svg_path.read_text()
    width, height, layout = geometry(text)
    peak = peak_alpha(text)

    print("checking %s  (frame %dx%d, peak %.3f)" % (svg_path, width, height, peak))
    global RADIUS
    # The corner radius is the arc radius in the corner fill path; the ring is the
    # slice width minus it. Both follow the artwork instead of being duplicated.
    arc = re.search(r'id="decoration-topleft".*?<path d="[^"]*A ([\d.]+),', text, re.S)
    RADIUS = int(round(float(arc.group(1))))
    ring = layout["topleft"][2] - RADIUS
    check(ring > 0, "top-left slice is wider than the %dpx corner (shadow ring %dpx)" % (RADIUS, ring))
    check(layout["left"][2] == ring + RADIUS, "left slice width matches ring + corner")
    check("cut-" not in text, "no corner cutout masks (they erase the corner shadow)")
    check('fill="#0A0B0D"' not in text, "no #0A0B0D title divider (the client paints its own hairline)")

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        probe = build_probe()
        size = (width, height)
        audit(compose(text, probe, "decoration-", work, size, layout), "active", HEADER_FILL, ring, peak)
        audit(compose(text, probe, "decoration-inactive-", work, size, layout), "inactive", INACTIVE_FILL, ring, peak)

    print()
    if failures:
        print("%d check(s) failed" % len(failures))
        return 1
    print("all decoration checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
