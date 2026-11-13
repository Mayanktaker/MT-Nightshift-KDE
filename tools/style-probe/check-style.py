#!/usr/bin/env python3
# © Mayanktaker Computers & Web Development | https://mayanktaker.com
# SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
# SPDX-License-Identifier: LGPL-2.0-or-later
"""Assert the rendered field family from render-fields output.

Usage: check-style.py <render-dir> [--ci]

--ci skips Breeze-dependent assertions (the frame-suppression check and the
12px scroll-bar extent) because CI has no Breeze style; the base style then is
Qt's fallback and those two checks would fail for the wrong reason.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    state = "OK" if ok else "FAIL"
    print(f"  {name:34s} {state} {detail}")
    if not ok:
        FAILURES.append(name)


def taper(path: Path) -> tuple[int, int]:
    alpha = np.array(Image.open(path).convert("RGBA").split()[3])
    ys, xs = np.where(alpha > 10)
    if len(xs) == 0:
        return 0, 0
    x0, y0 = int(xs.min()), int(ys.min())
    height = int(ys.max()) - y0 + 1
    recession = []
    for y in range(y0, y0 + height // 2):
        row = np.where(alpha[y] > 10)[0]
        if len(row):
            recession.append(int(row.min()) - x0)
    return height, (max(recession) if recession else 0)


def main() -> int:
    outdir = Path(sys.argv[1])
    ci = "--ci" in sys.argv[2:]

    # Corner language: every field-family pill must show the deep corner taper.
    for name in ["framed-lineedit", "framed-lineedit-focused", "editable-combo",
                 "editable-combo-focused", "selector-combo", "selector-combo-focused",
                 "spinbox", "spinbox-focused"]:
        path = outdir / f"{name}.png"
        height, recession = taper(path)
        check(f"{name} taper", recession >= 10, f"h={height} taper={recession}px")

    # Breeze's tight frame must not be stamped over our pill (needs Breeze).
    if not ci:
        frame_alpha = np.array(Image.open(outdir / "framed-lineedit-framecheck.png").convert("RGBA").split()[3])
        check("frame suppression", int(frame_alpha.max()) == 0, f"max alpha={int(frame_alpha.max())}")

    # Free-space meter: accent fill and a groove that is not a black slab.
    meter = np.array(Image.open(outdir / "capacity-meter-custom.png").convert("RGB")).astype(int)
    mid = meter.shape[0] // 2
    fill_blue = meter[mid, 4][2] > meter[mid, 4][0] + 60
    check("meter accent fill", fill_blue, f"rgb={tuple(meter[mid, 4])}")
    groove = meter[mid, 140]
    check("meter groove not black", int(groove.sum()) > 30, f"rgb={tuple(groove)}")

    # Focus ring: present, blue-family, and exactly one pixel wide at mid-height.
    focused = np.array(Image.open(outdir / "framed-lineedit-focused.png").convert("RGB")).astype(int)
    ring_row = focused[focused.shape[0] // 2]
    blues = [x for x in range(60) if ring_row[x][2] > ring_row[x][0] + 40]
    runs, current = [], 0
    previous = -2
    for x in blues:
        current = current + 1 if x == previous + 1 else 1
        runs.append(current)
        previous = x
    longest = max(runs) if runs else 0
    check("focus ring 1px", bool(runs) and longest <= 2, f"run={longest}px")

    # Disabled fields: lifted tone plus a dimmed hairline (settings pages grey
    # out whole groups — the shapes must stay legible without the focus ring).
    for name in ["disabled-combo", "disabled-editable-combo", "disabled-lineedit"]:
        disabled = np.array(Image.open(outdir / f"{name}.png").convert("RGB")).astype(int)
        dh, dw = disabled.shape[:2]
        fill = disabled[dh // 2, dw // 3]
        check(f"{name} lifted fill", int(fill.sum()) > 75 and abs(int(fill.sum()) - 34) > 12,
              f"rgb={tuple(fill)}")
        outline = disabled[dh // 2, 0]
        check(f"{name} dimmed outline", int(outline.sum()) > int(fill.sum()) + 8,
              f"outline={tuple(outline)}")

    # 12px scroll-bar gutter (needs Breeze's 21px to clamp down from).
    if not ci:
        scrollbar = np.array(Image.open(outdir / "scrollbar.png").convert("RGBA"))
        opaque_cols = np.where(scrollbar[:, :, 3].max(axis=0) > 10)[0]
        extent = (int(opaque_cols.max()) - int(opaque_cols.min()) + 1) if len(opaque_cols) else 0
        check("scrollbar 12px gutter", extent == 12, f"extent={extent}px")

    if FAILURES:
        print(f"style checks FAILED: {', '.join(FAILURES)}")
        return 1
    print("all style checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
