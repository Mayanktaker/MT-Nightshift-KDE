#!/usr/bin/env python3
# © Mayanktaker Computers & Web Development | https://mayanktaker.com
# SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
# SPDX-License-Identifier: LGPL-2.0-or-later
"""Assert the rendered field family from render-fields output.

Usage: check-style.py <render-dir> [--ci] --scheme <name>

--scheme names the colour scheme the render was produced under and selects its
reference tones from SCHEMES; it is required, because the item-view checks
measure ink against the palette the probe actually painted.

--ci skips Breeze-dependent assertions (frame suppression, the 12px scroll-bar
extent, and the menu size/corner scan) because that image has no Breeze style;
the base style is then Qt's fallback and those checks would fail for the wrong
reason. The Fedora CI job installs Breeze and runs the full set.
"""

from __future__ import annotations

import gzip
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

# Per-scheme reference tones. `window_rgb` is the Base tone a grabbed list or
# viewport paints, which is one step below Colors:Window; `pill_text_rgb` is the
# tone CE_ItemViewItem draws the selected row's text in, so it flips polarity on
# Nord Night and One Dark Pro; `accent_rgb` is the Selection background and
# `accent_blue` declares its blue-dominance, the premise behind every
# blue-family assertion below.
SCHEMES = {
    "MT-Nightshift": {
        "page_rgb": (16, 18, 22),
        "window_rgb": (10, 11, 13),
        "button_rgb": (27, 31, 37),
        "pill_text_rgb": (255, 255, 255),
        "accent_rgb": (31, 110, 156),
        "accent_blue": True,
    },
    "MT-Dayshift": {
        "page_rgb": (239, 241, 245),
        "window_rgb": (250, 251, 253),
        "button_rgb": (244, 246, 249),
        "pill_text_rgb": (255, 255, 255),
        "accent_rgb": (31, 110, 156),
        "accent_blue": True,
    },
    "MT-Nord-Night": {
        "page_rgb": (46, 52, 64),
        "window_rgb": (35, 41, 50),
        "button_rgb": (59, 66, 82),
        "pill_text_rgb": (46, 52, 64),
        "accent_rgb": (132, 165, 198),
        "accent_blue": True,
    },
    "MT-Nord-Day": {
        "page_rgb": (236, 239, 244),
        "window_rgb": (247, 249, 252),
        "button_rgb": (229, 233, 240),
        "pill_text_rgb": (255, 255, 255),
        "accent_rgb": (76, 107, 145),
        "accent_blue": True,
    },
    "MT-One-Dark-Pro": {
        "page_rgb": (40, 44, 52),
        "window_rgb": (29, 31, 35),
        "button_rgb": (64, 71, 84),
        "pill_text_rgb": (29, 31, 35),
        "accent_rgb": (82, 139, 255),
        "accent_blue": True,
    },
}

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    state = "OK" if ok else "FAIL"
    print(f"  {name:34s} {state} {detail}")
    if not ok:
        FAILURES.append(name)


def alpha_taper(alpha: np.ndarray) -> tuple[int, int]:
    """Height and maximum left-edge recession of the top-left quarter of a shape."""
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


def taper(path: Path) -> tuple[int, int]:
    return alpha_taper(np.array(Image.open(path).convert("RGBA").split()[3]))


def corner_recession(path: Path, corner: str) -> tuple[int, int]:
    """Measure any corner by mirroring it into the top-left position."""
    alpha = np.array(Image.open(path).convert("RGBA").split()[3])
    if "r" in corner:
        alpha = np.fliplr(alpha)
    if "b" in corner:
        alpha = np.flipud(alpha)
    return alpha_taper(alpha)


def shipped_corner_radius(path: Path) -> int:
    """Corner radius of the first top-left path in a shipped Plasma SVGZ.

    The panel and dialog frames draw a quarter arc, the popup frame a sampled
    polygon closing at the same two points; in both forms the radius is the
    reach along the two edges that meet the corner.
    """
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        svg = handle.read()
    group = svg.find('id="topleft"')
    if group < 0:
        return -1
    match = re.search(r'\bd="([^"]+)"', svg[group:])
    if not match:
        return -1
    numbers = [float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", match.group(1))]
    points = list(zip(numbers[0::2], numbers[1::2]))
    horizontal = [x for x, y in points if y <= 0.5]
    vertical = [y for x, y in points if x <= 0.5]
    return int(round(min(max(horizontal, default=0), max(vertical, default=0))))


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: check-style.py <render-dir> [--ci] --scheme <name>", file=sys.stderr)
        return 2
    outdir = Path(sys.argv[1])
    rest = sys.argv[2:]
    ci = "--ci" in rest
    scheme_name = None
    if "--scheme" in rest and rest.index("--scheme") + 1 < len(rest):
        scheme_name = rest[rest.index("--scheme") + 1]
    if scheme_name is None:
        print(f"--scheme is required; one of: {', '.join(SCHEMES)}", file=sys.stderr)
        return 2
    if scheme_name not in SCHEMES:
        print(f"unknown scheme {scheme_name!r}; one of: {', '.join(SCHEMES)}", file=sys.stderr)
        return 2
    scheme = SCHEMES[scheme_name]
    window_rgb = np.array(scheme["window_rgb"])
    pill_text_rgb = np.array(scheme["pill_text_rgb"])

    # Corner language: every field-family surface must show the shared 10px taper.
    for name in ["framed-lineedit", "framed-lineedit-focused", "framed-lineedit-hover",
                 "editable-combo", "editable-combo-focused", "selector-combo",
                 "selector-combo-focused", "selector-combo-hover", "spinbox",
                 "spinbox-focused", "spinbox-hover"]:
        path = outdir / f"{name}.png"
        height, recession = taper(path)
        check(f"{name} taper", height > 8 and 5 <= recession <= 8,
              f"h={height} taper={recession}px (5-8px for a 10px radius)")

    # QMenu outer corners keep their 15px popup radius, not the shared 10px
    # control radius. The menu's own size comes from the base style's metrics, so
    # on a CI image without Breeze the size and corner scan are skipped; the
    # Fedora job installs Breeze and runs them.
    menu_path = outdir / "menu.png"
    if not ci:
        menu_size = Image.open(menu_path).size
        check("menu dimensions", 60 <= menu_size[0] <= 80 and 90 <= menu_size[1] <= 110,
              f"size={menu_size} (60-80 x 90-110)")
        for corner in ("tl", "tr", "bl", "br"):
            height, recession = corner_recession(menu_path, corner)
            check(f"menu corner {corner} taper", height >= 80 and 12 <= recession <= 18,
                  f"h={height} taper={recession}px (12-18px popup radius)")

    sb_height, sb_taper = taper(outdir / "statusbar.png")
    check("statusbar corner taper", sb_height > 8 and sb_taper >= 8,
          f"h={sb_height} taper={sb_taper}px (>= 8px)")

    for state in ("active", "inactive"):
        th, tt = taper(outdir / f"tab-{state}.png")
        check(f"tab {state} corner taper", th > 8 and tt >= 8,
              f"h={th} taper={tt}px (>= 8px)")
        full = np.array(Image.open(outdir / f"tab-{state}.png").convert("RGB")).astype(int)
        shape = np.array(Image.open(outdir / f"tab-{state}-shape.png").convert("RGB")).astype(int)
        glyph_px = int((np.abs(full - shape).sum(axis=2) > 20).sum())
        check(f"tab {state} label drawn", glyph_px > 20,
              f"label diff px={glyph_px} (want > 20)")
    inactive_rgb = np.array(Image.open(outdir / "tab-inactive.png").convert("RGB")).astype(int)
    tones, counts = np.unique(inactive_rgb.reshape(-1, 3), axis=0, return_counts=True)
    dominant = tones[np.argmax(counts)]
    accent = scheme["accent_rgb"]
    check("tab inactive tone muted", int(np.abs(dominant - np.array(accent)).sum()) > 60,
          f"dominant={tuple(dominant)} accent={accent}")

    # Hovered menu row: the highlight is a tighter interaction pill, not Breeze's flat band.
    hover_height, hover_taper = taper(outdir / "menu-hover.png")
    check("menu hover pill taper", hover_height > 8 and 5 <= hover_taper < 14,
          f"h={hover_height} taper={hover_taper}px (5-13px)")
    hover_rgb = np.array(Image.open(outdir / "menu-hover.png").convert("RGB")).astype(int)
    on_pill = int((np.abs(hover_rgb - pill_text_rgb).sum(axis=2) < 120).sum())
    check("menu hover text on pill", on_pill > 20,
          f"pill-text px={on_pill} (want > 20)")

    for state in ("hover", "pressed", "checked"):
        h, t = taper(outdir / f"tool-{state}.png")
        check(f"tool {state} corner taper", h > 8 and 5 <= t < 14,
              f"h={h} taper={t}px (5-13px)")
    idle_height, idle_taper = taper(outdir / "tool-idle.png")
    check("tool idle unchanged", idle_taper < 8,
          f"h={idle_height} taper={idle_taper}px (Breeze idle surface, not our pill)")
    idle_rgb = np.array(Image.open(outdir / "tool-idle.png").convert("RGB")).astype(int)
    menu_rgb = np.array(Image.open(outdir / "tool-menu.png").convert("RGB")).astype(int)
    arrow_px = int((np.abs(idle_rgb[:, -25:] - menu_rgb[:, -25:]).sum(axis=2) > 20).sum())
    check("tool menu arrow drawn", arrow_px > 20, f"right-edge diff px={arrow_px}")

    # A focused check box must not wrap its label in a pill: the base style owns
    # that cue, and the chip itself carries the keyboard ring.
    focus_widget = np.array(Image.open(outdir / "focus-widget.png").convert("RGBA").split()[3])
    check("focus pill limited to item views", int(focus_widget.max()) == 0,
          f"max alpha={int(focus_widget.max())}")

    # Check/radio indicators: control-tone chips with a quiet hairline. The
    # Login Screen KCM mixes them with Breeze-drawn fields, so a bright Base
    # slab and a loud edge were the two visible inconsistencies.
    def indicator(name):
        return np.array(Image.open(outdir / f"{name}.png").convert("RGB")).astype(int)

    unchecked = indicator("indicator-unchecked")
    mid = unchecked.shape[0] // 2
    chip_fill = unchecked[mid, 3]
    button_rgb = np.array(scheme["button_rgb"])
    check("indicator control tone", int(np.abs(chip_fill - button_rgb).sum()) <= 9,
          f"rgb={tuple(chip_fill)} ref={tuple(button_rgb)}")
    chip_edge = unchecked[mid, 0]
    check("indicator hairline quiet", int(np.abs(chip_edge - chip_fill).sum()) <= 60,
          f"edge={tuple(chip_edge)} fill={tuple(chip_fill)}")
    # A 20px chip is too small for the taper metric: measure the corner cut
    # instead — rounded at all, but not a pill.
    chip_alpha = np.array(Image.open(outdir / "indicator-unchecked.png").convert("RGBA").split()[3])
    corner_open = int(chip_alpha[0, 0]) <= 10 and int(chip_alpha[1, 1]) > 0
    first_full = next((x for x in range(chip_alpha.shape[1]) if chip_alpha[0, x] >= 250), 99)
    check("indicator corner small", corner_open and 2 <= first_full <= 8,
          f"first-full={first_full}px (2-8px, not a pill)")
    focused_chip = indicator("indicator-focused")
    focused_edge = focused_chip[mid, 0]
    check("indicator focus ring", focused_edge[2] > focused_edge[0] + 40,
          f"edge={tuple(focused_edge)}")
    checked_chip = indicator("indicator-checked")
    checked_fill = checked_chip[mid, 0]
    check("indicator checked accent", int(np.abs(checked_fill - accent).sum()) < 30,
          f"rgb={tuple(checked_fill)} ref={tuple(accent)}")
    disabled_chip = indicator("indicator-disabled")
    disabled_fill = disabled_chip[mid, 3]
    page_rgb = np.array(scheme["page_rgb"])
    check("indicator disabled muted",
          int(np.abs(disabled_fill - page_rgb).sum()) < int(np.abs(chip_fill - page_rgb).sum()),
          f"disabled={tuple(disabled_fill)} enabled={tuple(chip_fill)} page={tuple(page_rgb)}")

    # Breeze's tight frame must not be stamped over our pill (needs Breeze).
    if not ci:
        frame_alpha = np.array(Image.open(outdir / "framed-lineedit-framecheck.png").convert("RGBA").split()[3])
        check("frame suppression", int(frame_alpha.max()) == 0, f"max alpha={int(frame_alpha.max())}")

    # Free-space meter: accent fill and a groove that is not a black slab.
    meter = np.array(Image.open(outdir / "capacity-meter-custom.png").convert("RGB")).astype(int)
    mid = meter.shape[0] // 2
    fill = meter[mid, 4]
    accent = np.array(scheme["accent_rgb"])
    accent_blue = fill[2] > fill[0] + 60
    check("meter accent fill",
          int(np.abs(fill - accent).sum()) < 30 and accent_blue == scheme["accent_blue"],
          f"rgb={tuple(fill)} ref={tuple(accent)}")
    groove = meter[mid, 140]
    check("meter groove not black", int(groove.sum()) > 30, f"rgb={tuple(groove)}")
    small_meter = np.array(Image.open(outdir / "capacity-meter-small-fill.png").convert("RGB")).astype(int)
    small_alpha = np.array(Image.open(outdir / "capacity-meter-small-fill.png").convert("RGBA").split()[3])
    small_blue = (small_meter[:, :, 2] > small_meter[:, :, 0] + 60) & (small_alpha > 10)
    top_fill = np.where(small_blue[0])[0]
    top_edge = int(top_fill.min()) if len(top_fill) else -1
    check("meter short fill stays rounded", 1 <= top_edge <= 4,
          f"first accent pixel at top edge={top_edge}px (1-4px, not a dot)")

    for hover_name, idle_name in [
        ("framed-lineedit-hover", "framed-lineedit"),
        ("selector-combo-hover", "selector-combo"),
        ("spinbox-hover", "spinbox"),
    ]:
        hover = np.array(Image.open(outdir / f"{hover_name}.png").convert("RGB")).astype(int)
        idle = np.array(Image.open(outdir / f"{idle_name}.png").convert("RGB")).astype(int)
        y = hover.shape[0] // 2
        edge_change = int(np.abs(hover[y, 0] - idle[y, 0]).sum())
        check(f"{hover_name} has hover outline", edge_change > 60,
              f"left-edge RGB change={edge_change} (want > 60)")

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
        check(f"{name} lifted fill",
              int(fill.sum()) > 75 and abs(int(fill.sum()) - int(window_rgb.sum())) > 12,
              f"rgb={tuple(fill)}")
        outline = disabled[dh // 2, 0]
        check(f"{name} dimmed outline", abs(int(outline.sum()) - int(fill.sum())) >= 8,
              f"outline={tuple(outline)}")

    # Item-view pills: selections and hovers are inset Highlight pills, inactive
    # selections are muted grey. Every hover path must carry the same taper.
    def pill_shape(path, blue_required):
        rgb = np.array(Image.open(path).convert("RGB")).astype(int)
        alpha = np.array(Image.open(path).convert("RGBA").split()[3])
        blue = (rgb[:, :, 2] > rgb[:, :, 0] + 60) & (alpha > 10)
        ys, xs = np.where(blue) if blue_required else (None, None)
        if blue_required:
            if len(ys) == 0:
                return False, "no accent fill"
            left_inset = int(xs.min())
            region = blue[:, max(0, left_inset):xs.max() + 1]
            rec = []
            for row in range(region.shape[0]):
                cols = np.where(region[row])[0]
                if len(cols):
                    rec.append(int(cols.min()))
            deepest = max(rec) if rec else 0
            return deepest >= 4 and left_inset >= 3, f"inset={left_inset} taper={deepest}"
        diff = np.abs(rgb - window_rgb).sum(axis=2)
        ink = (diff > 12) & (alpha > 10)
        if not ink.any():
            return False, "no ink"
        x0 = int(np.where(ink)[1].min())
        rec = []
        for row in range(ink.shape[0]):
            cols = np.where(ink[row])[0]
            if len(cols):
                rec.append(int(cols.min()) - x0)
        deepest = max(rec) if rec else 0
        return deepest >= 4 and x0 >= 3, f"inset={x0} taper={deepest}"

    for name, blue in [("item-selected", True), ("item-selected-palette-active", True),
                       ("item-hover", False), ("itemrow-hover", False),
                       ("item-ce-hover", False), ("item-selected-inactive", False)]:
        ok, detail = pill_shape(outdir / f"{name}.png", blue)
        check(f"{name} pill", ok, detail)

    idle_path = outdir / "itemrow-idle.png"
    idle_row = np.array(Image.open(idle_path).convert("RGB")).astype(int)
    idle_alpha = np.array(Image.open(idle_path).convert("RGBA").split()[3])
    idle_mask = ((np.abs(idle_row - window_rgb).sum(axis=2) > 12) & (idle_alpha > 10))
    check("itemrow idle unpainted", not idle_mask.any(),
          f"ink px={int(idle_mask.sum())}")

    # Item-view content: readable text stays on the accent pill (CE path). The
    # probe grabs the list over an opaque base, so the two most common exact
    # tones are that background and the pill surface; the pill's bounding box
    # isolates the selected row's text from every other row.
    content = np.array(Image.open(outdir / "itemview-selected.png").convert("RGB")).astype(int)
    tones, tone_counts = np.unique(content.reshape(-1, 3), axis=0, return_counts=True)
    base_tone, pill_tone = tones[np.argsort(-tone_counts)[0]], tones[np.argsort(-tone_counts)[1]]
    ys, xs = np.where((content == pill_tone).all(axis=2))
    row = content[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    on_pill = (np.abs(row - pill_text_rgb).sum(axis=2) < 180) \
        & (np.abs(row - pill_tone).sum(axis=2) > 40) \
        & (np.abs(row - base_tone).sum(axis=2) > 12)
    text_px = int(on_pill.sum())
    check("item text on pill", text_px > 40, f"text px={text_px}")

    # Boxed item-view frame: dimmed rounded hairline, not a blue square outline.
    frame = np.array(Image.open(outdir / "itemview-frame.png").convert("RGB")).astype(int)
    fh, fw = frame.shape[:2]
    border_row = frame[fh // 2, 0:12]
    blue_border = int((border_row[:, 2] > border_row[:, 0] + 40).sum())
    border_ink = int((np.abs(border_row - window_rgb).sum(axis=1) > 30).sum())
    check("item frame dimmed", border_ink > 0 and blue_border == 0,
          f"ink px={border_ink}, blue px={blue_border}")

    # Shipped frame geometry: measure the actual corner paths, never a
    # regenerated sample. Panel and dialog frames keep Breeze's 6px band; the
    # popup frame (widgets/background) is the 14px surface.
    for style in ["mt-nightshift", "mt-dayshift", "mt-nord-night", "mt-nord-day",
                  "mt-one-dark-pro"]:
        for relative, expected in [
            ("widgets/panel-background.svgz", 6),
            ("dialogs/background.svgz", 6),
            ("widgets/background.svgz", 14),
        ]:
            radius = shipped_corner_radius(Path("themes") / style / relative)
            check(f"{style} {relative} corner", radius == expected,
                  f"{radius}px (want {expected}px)")

    # Keyboard-focus pill: accent ring, pill-rounded, inset; hidden when selected.
    ring = np.array(Image.open(outdir / "focus-pill.png").convert("RGB")).astype(int)
    blue = (ring[:, :, 2] > ring[:, :, 0] + 60) & (ring.sum(axis=2) > 60)
    ys, xs = np.where(blue)
    ring_ok = len(ys) > 0
    detail = "no ring"
    if ring_ok:
        left_inset = int(xs.min())
        rec = []
        for row in range(blue.shape[0]):
            cols = np.where(blue[row])[0]
            if len(cols):
                rec.append(int(cols.min()) - left_inset)
        deepest = max(rec) if rec else 0
        ring_ok = left_inset >= 3 and deepest >= 5
        detail = f"inset={left_inset} taper={deepest}"
    check("focus pill ring", ring_ok, detail)

    selected_focus = np.array(Image.open(outdir / "focus-pill-selected.png").convert("RGB")).astype(int)
    suppressed = int(((selected_focus[:, :, 2] > selected_focus[:, :, 0] + 60)).sum()) == 0
    check("focus ring hidden when selected", suppressed)

    listview = np.array(Image.open(outdir / "itemview-selected.png").convert("RGB")).astype(int)
    hi_blue = (listview[:, :, 2] > listview[:, :, 0] + 60)
    cols = np.where(hi_blue.any(axis=0))[0]
    check("list selection pill", len(cols) > 0 and int(cols.min()) >= 3,
          f"fill cols {int(cols.min())}-{int(cols.max())}" if len(cols) else "none")

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
