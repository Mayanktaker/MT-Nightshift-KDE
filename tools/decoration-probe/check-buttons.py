#!/usr/bin/env python3
# © Mayanktaker Computers & Web Development | https://mayanktaker.com
# SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development
# SPDX-License-Identifier: LGPL-2.0-or-later
"""Palette and geometry checks for the generated Aurorae button artwork.

A copied button file can parse as valid XML and still be unreadable: the
2026-11 review found Dayshift shipping Nightshift's light-grey glyphs against
its own light header. This script therefore reads the committed state groups,
compares every tone with its variant's palette and measures contrast against
that variant's header, instead of trusting the file to exist.

It also proves the shared-geometry promise: all four variants must have
identical paths, rects and stroke widths for each button, so a colour fix can
never quietly move a glyph. The decoration titles are checked here too, since
inherited "MT Nightshift" titles are the same copy defect.

Palettes come from build-decoration.py itself, so the check cannot drift from
the generator.

Usage: check-buttons.py
Exit status is 1 when a check fails.
"""

from __future__ import annotations

import importlib.util
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUTTONS = ("close", "minimize", "maximize", "restore", "menu")
GEOMETRY_ATTRS = ("d", "x", "y", "width", "height", "rx", "stroke-width",
                  "stroke-linecap", "stroke-linejoin")
SHAPE_TAGS = {"path", "rect"}

failures: list[str] = []


def check(condition: bool, message: str) -> bool:
    """Record one assertion; only failures are printed, at the end."""
    if not condition:
        failures.append(message)
    return condition


def load_generator():
    """Import build-decoration.py despite the hyphen in its filename."""
    spec = importlib.util.spec_from_file_location("build_decoration",
                                                  HERE / "build-decoration.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def luminance(colour: str) -> float:
    """WCAG 2.1 relative luminance of a #RRGGBB string."""
    channels = []
    for offset in (1, 3, 5):
        value = int(colour[offset:offset + 2], 16) / 255.0
        channels.append(value / 12.92 if value <= 0.04045
                        else ((value + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast(first: str, second: str) -> float:
    """WCAG 2.1 contrast ratio between two #RRGGBB colours."""
    high, low = sorted((luminance(first), luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def local(tag: str) -> str:
    """Element name without the SVG namespace."""
    return tag.rsplit("}", 1)[-1]


def state_groups(root) -> dict[str, object]:
    """Every element carrying an id, keyed by that id."""
    return {element.get("id"): element for element in root.iter() if element.get("id")}


def tones(element) -> tuple[set[str], set[str]]:
    """Non-'none' stroke and fill colours inside one state group.

    Hex colours are normalised to upper case; gradient references stay as-is.
    """
    strokes, fills = set(), set()
    for child in element.iter():
        for attribute, bucket in (("stroke", strokes), ("fill", fills)):
            value = child.get(attribute)
            if value and value != "none":
                bucket.add(value.upper() if value.startswith("#") else value)
    return strokes, fills


def ring_stroke(element) -> str | None:
    """The stroke of one state group's 19px, 1px-wide hover ring."""
    for child in element.iter():
        if (local(child.tag) == "rect" and child.get("fill") == "none"
                and child.get("stroke-width") == "1"):
            stroke = child.get("stroke")
            return stroke.upper() if stroke else None
    return None


def geometry(root) -> list[tuple[str, tuple[str | None, ...]]]:
    """Every shape's geometry, with colour attributes deliberately excluded."""
    return [(local(element.tag), tuple(element.get(attribute) for attribute in GEOMETRY_ATTRS))
            for element in root.iter() if local(element.tag) in SHAPE_TAGS]


def expected_tones(palette: dict[str, str], blend,
                   deactivated_mix: float) -> dict[str, tuple[set[str], set[str]]]:
    """What each state group must paint, from the variant palette alone."""
    disabled_active = blend(palette["header_active"], palette["foreground_inactive"],
                            deactivated_mix)
    disabled_inactive = blend(palette["header_inactive"], palette["foreground_inactive"],
                              deactivated_mix)
    return {
        "active": ({palette["foreground"]}, set()),
        "hover": ({palette["negative"]}, set()),
        "pressed": ({palette["selection_text"]}, {palette["selection"]}),
        "deactivated": ({disabled_active}, set()),
        "inactive": ({palette["foreground_inactive"]}, set()),
        "hover-inactive": ({palette["foreground_inactive"]}, set()),
        "pressed-inactive": ({palette["selection_text"]}, {palette["selection"]}),
        "deactivated-inactive": ({disabled_inactive}, set()),
    }


def check_button(path: Path, label: str, palette: dict[str, str], title: str,
                 others: list[str], blend, mix: float) -> list | None:
    """Parse one button, assert its title, tones and contrast; return geometry."""
    if not check(path.exists(), "%s is missing" % path):
        return None
    text = path.read_text()
    try:
        root = ET.fromstring(text)
    except ET.ParseError as error:
        check(False, "%s does not parse as XML (%s)" % (path, error))
        return None
    check(local(root.tag) == "svg", "%s root element is <svg>" % path)
    check("GENERATED FILE" in text, "%s is generated, not a hand copy" % path)

    headings = [node.text or "" for node in root.iter() if local(node.tag) == "title"]
    check(headings == ["%s %s button" % (title, label)],
          "%s title names %r (got %r)" % (path, "%s %s button" % (title, label), headings))
    check("%s Aurorae %s button." % (title, label) in text,
          "%s comment names %s" % (path, title))
    for other in others:
        check(other not in text, "%s does not inherit %r" % (path, other))

    groups = state_groups(root)
    wanted = expected_tones(palette, blend, mix)
    for state, (want_strokes, want_fills) in wanted.items():
        element = groups.get(state + "-center")
        if not check(element is not None, "%s has a %s state group" % (path, state)):
            continue
        strokes, fills = tones(element)
        check(strokes == {value.upper() for value in want_strokes},
              "%s %s strokes %s match the palette (got %s)"
              % (path, state, sorted(want_strokes), sorted(strokes)))
        check(fills == {value.upper() for value in want_fills},
              "%s %s fills %s match the palette (got %s)"
              % (path, state, sorted(want_fills), sorted(fills)))

    allowed = {value.upper()
               for strokes, fills in wanted.values()
               for value in strokes | fills}
    used = set()
    for child in root.iter():
        for attribute in ("stroke", "fill"):
            value = child.get(attribute)
            if value and value != "none":
                used.add(value.upper())
    check(used <= allowed, "%s uses only palette tones (stray %s)" % (path, sorted(used - allowed)))

    # Real colours, not XML shape: the light-header defect was a 1.5:1 glyph.
    floors = (
        (palette["foreground"], palette["header_active"], 4.5, "active glyph"),
        (palette["foreground_inactive"], palette["header_active"], 3.0, "inactive glyph"),
        (palette["negative"], palette["header_active"], 3.0, "hover glyph/outline"),
        (palette["foreground_inactive"], palette["header_inactive"], 3.0,
         "hover-inactive ring and glyph"),
        (palette["selection_text"], palette["selection"], 4.5, "pressed glyph"),
    )
    for colour, surface, floor, role in floors:
        ratio = contrast(colour, surface)
        check(ratio >= floor, "%s %s on %s is %.2f:1 (floor %.1f:1)"
              % (path, role, surface, ratio, floor))

    # The hover-inactive ring is the only cue on an inactive window, so assert
    # the element that actually paints it, against the surface it sits on.
    hover_inactive = groups.get("hover-inactive-center")
    if check(hover_inactive is not None, "%s has a hover-inactive state group" % path):
        ring = ring_stroke(hover_inactive)
        check(ring == palette["foreground_inactive"].upper(),
              "%s hover-inactive ring is ForegroundInactive (got %s)" % (path, ring))
        ratio = contrast(palette["foreground_inactive"], palette["header_inactive"])
        check(ratio >= 3.0, "%s hover-inactive ring on %s is %.2f:1 (floor 3.0:1)"
              % (path, palette["header_inactive"], ratio))
    return geometry(root)


def check_decoration(path: Path, palette: dict[str, str], title: str,
                     others: list[str]) -> None:
    """Parse the decoration and assert its title and baked surface tones."""
    if not check(path.exists(), "%s is missing" % path):
        return
    text = path.read_text()
    try:
        root = ET.fromstring(text)
    except ET.ParseError as error:
        check(False, "%s does not parse as XML (%s)" % (path, error))
        return
    check("GENERATED FILE" in text, "%s is generated, not a hand copy" % path)
    headings = [node.text or "" for node in root.iter() if local(node.tag) == "title"]
    check(headings == ["%s window decoration" % title],
          "%s title names %r (got %r)" % (path, "%s window decoration" % title, headings))
    for other in others:
        check(other not in text, "%s does not inherit %r" % (path, other))

    for group_id, expected in (("decoration-top", palette["header_active"]),
                               ("decoration-inactive-top", palette["header_inactive"]),
                               ("decoration-maximized-center", palette["header_active"]),
                               ("decoration-maximized-inactive-center", palette["header_inactive"])):
        element = state_groups(root).get(group_id)
        if not check(element is not None, "%s has a %s group" % (path, group_id)):
            continue
        _, fills = tones(element)
        check(expected.upper() in fills,
              "%s %s paints %s (got %s)" % (path, group_id, expected, sorted(fills)))

    # The frame line is a deliberate whisper, so it only has to differ from the
    # header fill; its 3:1 duty does not apply (it is not a state cue).
    line, header = palette["frame_line"], palette["header_active"]
    check(max(abs(int(line[i:i + 2], 16) - int(header[i:i + 2], 16))
              for i in (1, 3, 5)) >= 4,
          "%s frame line is distinguishable from the header fill" % path)


def main() -> int:
    """Run the palette and geometry checks for every registered variant."""
    generator = load_generator()
    baseline: dict[str, list] = {}
    names = list(generator.VARIANTS)
    for name in names:
        spec = generator.VARIANTS[name]
        palette, title = spec["palette"], spec["title"]
        others = [generator.VARIANTS[other]["title"] for other in names
                  if generator.VARIANTS[other]["title"] != title]
        directory = spec["out"].parent
        for button in BUTTONS:
            shapes = check_button(directory / (button + ".svg"),
                                  generator.BUTTON_LABELS[button], palette, title,
                                  others, generator.blend,
                                  generator.PARAMS["deactivated_mix"])
            if shapes is None:
                continue
            if button not in baseline:
                baseline[button] = shapes
            else:
                check(shapes == baseline[button],
                      "%s shares %s's geometry (only colours may vary)"
                      % (directory / (button + ".svg"), button))
        check_decoration(spec["out"], palette, title, others)
        print("  checked %s: 5 buttons, 8 states, decoration title" % title)

    if failures:
        print("\n".join("  FAIL " + message for message in failures))
        print("\n%d check(s) failed" % len(failures))
        return 1
    print("all %d variants' button tones, geometry and titles match their palettes"
          % len(names))
    return 0


if __name__ == "__main__":
    sys.exit(main())
