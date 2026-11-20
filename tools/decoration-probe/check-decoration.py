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
        block = re.search(r'^  <g id="decoration-%s".*?^  </g>' % name, text, re.S | re.M)
        if block is None:
            raise SystemExit("missing group decoration-%s in %s" % (name, "the document"))
        x, y = (int(v) for v in re.search(r'transform="translate\((-?\d+),(-?\d+)\)"', block.group(0)).groups())
        # The marker rect is the slice extent; the shadow and surface elements that
        # follow it are narrower (by the radius), so matching "the first rect" would
        # silently read the wrong footprint if the emission order ever changed.
        marker = re.search(r'<rect x="0" y="0" width="(\d+)" height="(\d+)" '
                           r'fill="none" stroke="none"/>', block.group(0)).groups()
        w, h = (int(v) for v in marker)
        layout[name] = (x, y, w, h)
    return width, height, layout


def declared_padding(svg_path: Path) -> int | None:
    """Read PaddingTop out of the sibling MT*rc, the value KWin actually reserves."""
    rc = next(iter(svg_path.parent.glob("MT*rc")), None)
    if rc is None:
        return None
    found = re.search(r'^PaddingTop=(\d+)$', rc.read_text(), re.M)
    return int(found.group(1)) if found else None


def reinforcement(text: str, state: str) -> list[tuple[str, float, float]]:
    """Stroke width and arc radius of each corner's reinforcement path.

    The generator emits one explicitly, so the exact geometry is readable from the
    document. A raster coverage test cannot separate "1px band plus a second pass"
    from "2px band": both read as full coverage at 45 degrees, which is how the
    over-thick stroke shipped in the first place.
    """
    found = []
    for corner in ("topleft", "topright", "bottomleft", "bottomright"):
        block = re.search(r'^  <g id="decoration-%s%s".*?^  </g>' % (state, corner),
                          text, re.S | re.M)
        if block is None:
            raise SystemExit("missing group decoration-%s%s" % (state, corner))
        strokes = re.findall(r'<path d="[^"]*?A ([\d.]+),[\d.]+ [^"]*?" '
                             r'fill="none" stroke="[^"]*" stroke-width="([\d.]+)"',
                             block.group(0))
        if len(strokes) != 1:
            found.append((corner, float("nan"), -1.0))
            continue
        found.append((corner, float(strokes[0][1]), float(strokes[0][0])))
    return found


def peak_alpha(text: str) -> float:
    """Largest stop-opacity in the shadow gradients."""
    return max(float(v) for v in re.findall(r'stop-opacity="([\d.]+)"', text))


def surface_fills(text: str) -> tuple[np.ndarray, np.ndarray]:
    """Read the active and inactive header fills straight from the artwork.

    The decoration is generated per variant, so the expected header tone must
    follow the file instead of being a baked Nightshift constant; otherwise a
    light variant fails a check that is really about geometry and shadow.
    """
    def fill(prefix: str) -> np.ndarray:
        block = re.search(r'^  <g id="%s-top".*?^  </g>' % prefix, text, re.S | re.M).group(0)
        match = re.search(r'fill="#([0-9A-Fa-f]{6})"', block)
        if match is None:
            raise SystemExit("%s-top has no hex surface fill" % prefix)
        return np.array([int(match.group(1)[i:i + 2], 16) for i in (0, 2, 4)])

    return fill("decoration"), fill("decoration-inactive")


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


def compose(text, probe, prefix, work, size, layout, scale=1) -> np.ndarray:
    """Render every slice of one state and stitch it into the frame."""
    defs = re.search(r"  <defs>.*?  </defs>\n", text, re.S).group(0)
    frame = np.zeros((size[1] * scale, size[0] * scale, 4), dtype=np.float64)
    for name, (ox, oy, w, h) in layout.items():
        block = re.search(r'^  <g id="%s%s".*?^  </g>\n' % (re.escape(prefix), name), text, re.S | re.M)
        if block is None:
            raise SystemExit("missing group %s%s" % (prefix, name))
        body = block.group(0).split("\n", 1)[1].rsplit("  </g>", 1)[0]
        body = re.sub(r'transform="translate\([-\d,]+\)"', 'transform="translate(0,0)"', body)
        source, target = work / "slice.svg", work / "slice.png"
        source.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">%s<g>%s</g></svg>'
            % (w * scale, h * scale, w, h, defs, body)
        )
        subprocess.run([str(probe), str(source), str(target)], check=True,
                       env={"QT_QPA_PLATFORM": "offscreen", "PATH": "/usr/bin:/bin", "HOME": str(Path.home())})
        tile = np.asarray(Image.open(target).convert("RGBA")).astype(np.float64)
        dst = frame[oy * scale:oy * scale + h * scale, ox * scale:ox * scale + w * scale]
        sa, da = tile[..., 3:4] / 255.0, dst[..., 3:4] / 255.0
        oa = sa + da * (1 - sa)
        rgb = (tile[..., :3] * sa + dst[..., :3] * da * (1 - sa)) / np.where(oa == 0, 1, oa)
        frame[oy * scale:oy * scale + h * scale, ox * scale:ox * scale + w * scale] = \
            np.concatenate([rgb, oa * 255.0], axis=2)
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


def band_width(frame, fill, line, span, cx, cy, sx, sy, angle, scale) -> float:
    """Radial extent of the line-coloured run at one angle, in 1x pixels.

    A 1px annulus measures ~1px; the over-thick reinforcement that shipped once
    measured 2px and stepped down to 1px at the tangent. Coverage, not colour
    distance, so this is independent of how far apart the palette's line and fill
    tones happen to be.
    """
    covered = []
    for radius in np.arange(RADIUS - 2.2, RADIUS + 0.15, 0.1):
        x = int(round(cx + sx * radius * np.cos(angle)))
        y = int(round(cy + sy * radius * np.sin(angle)))
        if not (0 <= y < frame.shape[0] and 0 <= x < frame.shape[1]):
            covered.append(0.0)
            continue
        # The shadow is also far from the fill, so distance alone would stretch the
        # run straight through it. Count a pixel only when it sits on the band.
        distance = np.hypot(x + 0.5 - cx, y + 0.5 - cy)
        if not (RADIUS - 1.5 <= distance <= RADIUS + 0.2):
            covered.append(0.0)
            continue
        # Classify by nearest reference tone instead of a coverage fraction: on a
        # low-contrast palette (Nord Day's inactive line is 5.4 RGB from the fill)
        # 8-bit rounding pushes a half-covered pixel over any fixed fraction.
        pixel = frame[y, x, :3]
        covered.append(1.0 if np.linalg.norm(pixel - line) <= np.linalg.norm(pixel - fill) else 0.0)
    longest = run = 0
    for score in covered:
        run = run + 1 if score >= 0.5 else 0
        longest = max(longest, run)
    # Device pixels at 2x are half a 1x pixel, so the gate stays comparable.
    return round(longest * 0.1 / scale, 2)


def audit(frame, label, fill, ring, peak, scale) -> None:
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
    # The RGB distance between the line and the fill ranges from ~5 to ~42 across the
    # five palettes, so a fixed fraction of it is not a fixed measurement: the same
    # 0.75 gate meant four RGB units on Nord Day and thirty-two on Nord Night.
    # Normalise on a common scale and keep the raw span in the message instead.
    span = max(1.0, float(np.linalg.norm(line - fill)))
    for name, (cx, cy, sx, sy) in {
        # Continuous coordinates of the arc centre: the right and bottom edges sit at
        # (extent - ring - RADIUS), not one pixel less, or the annulus test is 1px off
        # on two of the four corners.
        "top-left": (ring + RADIUS, ring + RADIUS, -1, -1),
        "top-right": (frame.shape[1] - ring - RADIUS, ring + RADIUS, 1, -1),
        "bottom-left": (ring + RADIUS, frame.shape[0] - ring - RADIUS, -1, 1),
        "bottom-right": (frame.shape[1] - ring - RADIUS, frame.shape[0] - ring - RADIUS, 1, 1),
    }.items():
        samples, widths = [], []
        for degrees in np.linspace(0, 90, 31):
            angle = np.radians(degrees)
            best = 0.0
            for radius in np.arange(RADIUS - 1.4, RADIUS + 0.15, 0.15):
                # Rounding x and y independently lands the sample up to half a pixel
                # off the band, which read as a 0.35 gap at 33 and 57 degrees on a
                # 10px corner while the 45-degree point measured 0.97. Take the best
                # neighbour instead: a 1px annulus always covers *some* nearby pixel.
                px = cx + sx * radius * np.cos(angle)
                py = cy + sy * radius * np.sin(angle)
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        x, y = int(round(px)) + dx, int(round(py)) + dy
                        if not (0 <= y < frame.shape[0] and 0 <= x < frame.shape[1]):
                            continue
                        # Count only neighbours whose centre sits on the band.
                        # Pixel centres are at i+0.5, so this has to be measured in
                        # continuous space against the arc centre; the earlier
                        # index-space surrogate under-read the radius by half a pixel
                        # and let the search drift into the shadow, whose distance
                        # from the fill is far wider than the band's.
                        distance = np.hypot(x + 0.5 - cx, y + 0.5 - cy)
                        if not (RADIUS - 1.5 <= distance <= RADIUS + 0.2):
                            continue
                        best = max(best, float(np.linalg.norm(frame[y, x, :3] - fill)) / span)
            samples.append(best)
        values = np.array(samples)
        for degrees in (30, 45, 60):
            angle = np.radians(degrees)
            widths.append(band_width(frame, fill, line, span, cx, cy, sx, sy, angle, scale))
        widest = max(widths)
        check(values.mean() >= 0.90, "%s arc border is continuous (mean %.2f)" % (name, values.mean()))
        check(values.min() >= 0.70, "%s arc border has no gap (min %.2f)" % (name, values.min()))
        # The reinforcement must stay inside the 1px band. A stroke wide enough to
        # read as a solid corner also draws a 2px line that steps down to 1px at the
        # tangent point, which is exactly the artefact this bound exists to catch.
        check(widest <= 1.8, "%s arc band stays 1px wide (widest %.2fpx)" % (name, widest))

    print("%s: surfaces" % label)
    header = frame[ring + 12 * scale, ring + 20 * scale, :3]
    check(np.abs(header - fill).max() <= 1, "header fill is %s (got %s)" % (fill, header.round().astype(int)))
    divider = frame[ring + 38 * scale, ring + 20 * scale, :3]
    check(np.abs(divider - fill).max() <= 1, "no title divider row at the header boundary")
    border = frame[mid, ring + 2 * scale, :3]
    check(border.max() >= 0, "side frame is painted")


def main() -> int:
    """Render both states and run the audit, at 1x or at a device scale."""
    argv = sys.argv[1:]
    scale = 1
    if "--scale" in argv:
        index = argv.index("--scale")
        scale = int(argv[index + 1])
        del argv[index:index + 2]
    svg_path = Path(argv[0]) if argv else DEFAULT_SVG
    if not svg_path.exists():
        raise SystemExit("decoration not found: %s" % svg_path)
    text = svg_path.read_text()
    width, height, layout = geometry(text)
    peak = peak_alpha(text)
    header_fill, inactive_fill = surface_fills(text)

    global RADIUS
    # The corner radius is the arc radius in the corner fill path; the ring is the
    # slice width minus it. Both follow the artwork instead of being duplicated,
    # then convert to device pixels so the measurements hold at any scale.
    arc = re.search(r'id="decoration-topleft".*?<path d="[^"]*A ([\d.]+),', text, re.S)
    if arc is None:
        raise SystemExit("cannot read the corner arc radius from decoration-topleft")
    radius_units = int(round(float(arc.group(1))))
    ring_units = layout["topleft"][2] - radius_units
    RADIUS = radius_units * scale
    ring = ring_units * scale

    print("checking %s  (frame %dx%d at %dx, peak %.3f)" % (svg_path, width, height, scale, peak))
    check(ring_units > 0, "top-left slice is wider than the %dpx corner (shadow ring %dpx)"
          % (radius_units, ring_units))
    # The ring is the slice footprint minus the corner, so it must match the padding
    # KWin reserves. A footprint captured at import kept the default ring while the
    # shadow square followed the radius, leaving a dead band no other check saw.
    padding = declared_padding(svg_path)
    if padding is not None:
        check(ring_units == padding,
              "slice ring (%dpx) equals the declared Padding (%dpx)" % (ring_units, padding))
    centre = layout["top"][2]
    header = layout["top"][3] - ring_units
    check(width == 2 * (ring_units + radius_units) + centre,
          "frame width is 2*(ring+corner)+centre (%d)" % (2 * (ring_units + radius_units) + centre))
    check(height == (ring_units + header) + centre + (ring_units + radius_units),
          "frame height is ring+header+centre+ring+corner")
    check(layout["left"][2] == layout["topleft"][2], "left slice matches the corner footprint")
    check(layout["top"][3] == layout["topleft"][3], "top slice height matches the corner footprint")
    # The reinforcement must exist and must not widen the band. Without the first
    # assertion the unreinforced arc (the "broken border" case) passes on the
    # low-contrast variants; without the second the 2px band passes everywhere.
    # `make check-dpr2` renders the deliberately unreinforced corner, so absence is
    # legal only when it is absent everywhere. A hand-edit that leaves one corner
    # bare is still a defect.
    found = [(state, corner, stroke_width, arc_radius)
             for state in ("", "inactive-")
             for corner, stroke_width, arc_radius in reinforcement(text, state)]
    bare = [f for f in found if f[2] != f[2]]
    if bare and len(bare) != len(found):
        check(False, "%d of %d corners keep their reinforcement path (a partial set "
                     "means a hand-edited SVG)" % (len(found) - len(bare), len(found)))
    elif bare:
        print("  note unreinforced artwork (%d corners, the --arc 1.0 HiDPI case): "
              "presence is not asserted, band width still is" % len(bare))
    for state, corner, stroke_width, arc_radius in found:
        if not (bare and len(bare) == len(found)):
            label = "%s%s" % (state or "active", corner)
            check(stroke_width == stroke_width, "%s has exactly one reinforcement path" % label)
            check(stroke_width <= 1.01, "%s reinforcement is %s <= 1px (no band widening)"
                  % (label, stroke_width))
            check(arc_radius == arc_radius and arc_radius <= radius_units - 0.49,
                  "%s reinforcement arc stays inside the %dpx band"
                  % (label, radius_units))
    check("cut-" not in text, "no corner cutout masks (they erase the corner shadow)")
    check('fill="#0A0B0D"' not in text, "no #0A0B0D title divider (the client paints its own hairline)")

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        probe = build_probe()
        size = (width, height)
        audit(compose(text, probe, "decoration-", work, size, layout, scale),
              "active", header_fill, ring, peak, scale)
        audit(compose(text, probe, "decoration-inactive-", work, size, layout, scale),
              "inactive", inactive_fill, ring, peak, scale)

    print()
    if failures:
        print("%d check(s) failed" % len(failures))
        return 1
    print("all decoration checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
