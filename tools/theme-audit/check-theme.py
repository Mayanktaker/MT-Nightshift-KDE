#!/usr/bin/env python3
# © Mayanktaker Computers & Web Development | https://mayanktaker.com
# SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development
# SPDX-License-Identifier: LGPL-2.0-or-later
"""Audit the shipped package metadata and palettes; exit 1 on any failure.

Three defect classes have actually shipped here, and all three are mechanical:
a palette copy that drifted from the scheme it mirrors (the dimmed negative and
the unified View alternate reached only one of three copies), a semantic colour
dimmed below the contrast floor the documentation promises, and package
versions that disagreed. This script re-derives each invariant from the files
so `make check` catches them instead of a review.

Checks
  * every palette copy of a variant is byte-identical to its scheme;
  * style / Look-and-Feel / Aurorae metadata agree on id, name and version;
  * the Qt style project version agrees with the shipped packages;
  * the Look-and-Feel selects the scheme, Plasma Style, style key and
    decoration the variant actually ships;
  * every Foreground* role clears the contrast floor against *both*
    backgrounds of its group, and the accent rings clear the non-text floor;
  * the Aurorae `.rc` padding and border match the artwork generator.

Run from anywhere: paths resolve against the repository root.
"""

from __future__ import annotations

import configparser
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FLOOR = 4.66  # design.md: lowest permitted Foreground* ratio, with margin over AA
NON_TEXT_FLOOR = 3.0  # design.md: outlines and indicators
EPS = 0.005  # allows a colour that rounds to exactly 4.66:1

GROUPS = [
    ("Colors:Button", "Button"),
    ("Colors:Complementary", "Complementary"),
    ("Colors:Header", "Header"),
    ("Colors:Header][Inactive", "Header[Inactive]"),
    ("Colors:Selection", "Selection"),
    ("Colors:Tooltip", "Tooltip"),
    ("Colors:View", "View"),
    ("Colors:Window", "Window"),
]
ROLES = [
    "ForegroundNormal",
    "ForegroundInactive",
    "ForegroundActive",
    "ForegroundLink",
    "ForegroundVisited",
    "ForegroundNegative",
    "ForegroundNeutral",
    "ForegroundPositive",
]
SELECTOR_GROUPS = ["Colors:Window", "Colors:Button"]

VARIANTS = [
    {
        "name": "Nightshift",
        "style_id": "mt-nightshift",
        "scheme": "color-schemes/MT-Nightshift.colors",
        "style": "themes/mt-nightshift",
        "laf": "themes/mt-nightshift-global",
        "aurorae": "themes/aurorae/MTNightshift",
    },
    {
        "name": "Dayshift",
        "style_id": "mt-dayshift",
        "scheme": "color-schemes/MT-Dayshift.colors",
        "style": "themes/mt-dayshift",
        "laf": "themes/mt-dayshift-global",
        "aurorae": "themes/aurorae/MTDayshift",
    },
    {
        "name": "NordNight",
        "style_id": "mt-nord-night",
        "scheme": "color-schemes/MT-Nord-Night.colors",
        "style": "themes/mt-nord-night",
        "laf": "themes/mt-nord-night-global",
        "aurorae": "themes/aurorae/MTNordNight",
    },
    {
        "name": "NordDay",
        "style_id": "mt-nord-day",
        "scheme": "color-schemes/MT-Nord-Day.colors",
        "style": "themes/mt-nord-day",
        "laf": "themes/mt-nord-day-global",
        "aurorae": "themes/aurorae/MTNordDay",
    },
    {
        "name": "One Dark Pro",
        "style_id": "mt-one-dark-pro",
        "scheme": "color-schemes/MT-One-Dark-Pro.colors",
        "style": "themes/mt-one-dark-pro",
        "laf": "themes/mt-one-dark-pro-global",
        "aurorae": "themes/aurorae/MTOneDarkPro",
    },
]

FAILURES: list[str] = []
QUIET = False
CHECKS = 0


def check(label: str, ok: bool, detail: str = "") -> bool:
    """Record one assertion; print it unless --quiet, but always print failures."""
    global CHECKS
    CHECKS += 1
    if not ok or not QUIET:
        print(f"  {label:44s} {'OK' if ok else 'FAIL'} {detail}")
    if not ok:
        FAILURES.append(label)
    return ok


def config(path: Path) -> configparser.ConfigParser:
    """Parses a KDE config file; `[Group][Sub]` stays one literal section name."""
    parser = configparser.ConfigParser(strict=False, interpolation=None)
    parser.optionxform = str
    parser.read(path, encoding="utf-8")
    return parser


def aurorae_id(variant: dict) -> str:
    """The Aurorae id is the package directory name, not its display name."""
    return Path(variant["aurorae"]).name


def luminance(rgb: tuple[int, int, int]) -> float:
    """WCAG 2.1 relative luminance of an sRGB colour."""

    def linear(channel: int) -> float:
        value = channel / 255.0
        return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4

    red, green, blue = (linear(channel) for channel in rgb)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast(first: tuple[int, int, int], second: tuple[int, int, int]) -> float:
    """WCAG 2.1 contrast ratio, unrounded."""
    high, low = (luminance(c) for c in (first, second))
    high, low = max(high, low), min(high, low)
    return (high + 0.05) / (low + 0.05)


def rgb(value: str) -> tuple[int, int, int]:
    """Parses a KDE `r,g,b` triple."""
    return tuple(int(part) for part in value.split(","))  # type: ignore[return-value]


def hexed(value: tuple[int, int, int]) -> str:
    """Formats a colour for the report."""
    return "#%02X%02X%02X" % value


def audit_palette(variant: dict) -> None:
    """Checks the contrast floors of one scheme, group by group."""
    path = ROOT / variant["scheme"]
    scheme = config(path)
    floor_pairs: list[tuple[float, str, str]] = []
    for section, label in GROUPS:
        if section not in scheme:
            check(f"{variant['name']} group {label}", False, "missing")
            continue
        backgrounds = [rgb(scheme[section][key]) for key in ("BackgroundNormal", "BackgroundAlternate")]
        for role in ROLES:
            if role not in scheme[section]:
                check(f"{variant['name']} {label}/{role}", False, "missing")
                continue
            colour = rgb(scheme[section][role])
            # Both backgrounds of the owning group are live: rows, strips and
            # raised controls use the alternate.
            worst = min(contrast(colour, background) for background in backgrounds)
            floor_pairs.append((worst, label, role))

    floor_pairs.sort()
    lowest = floor_pairs[0]
    check(
        f"{variant['name']} text contrast floor {FLOOR}:1",
        lowest[0] >= FLOOR - EPS,
        f"{lowest[0]:.2f} ({lowest[1]}/{lowest[2].removeprefix('Foreground')}), "
        f"{len(floor_pairs)} pairs",
    )
    if not QUIET:
        for ratio, label, role in floor_pairs[:3]:
            print(f"      lowest: {ratio:5.2f}  {label:<17} {role}")

    for section in SELECTOR_GROUPS:
        label = dict(GROUPS)[section]
        surface = rgb(scheme[section]["BackgroundNormal"])
        for key in ("DecorationFocus", "DecorationHover"):
            ratio = contrast(rgb(scheme[section][key]), surface)
            check(
                f"{variant['name']} {label}/{key.removeprefix('Decoration')} ring {NON_TEXT_FLOOR}:1",
                ratio >= NON_TEXT_FLOOR - EPS,
                f"{ratio:.2f} on {hexed(surface)}",
            )

    window = rgb(scheme["Colors:Window"]["BackgroundNormal"])
    selection = rgb(scheme["Colors:Selection"]["BackgroundNormal"])
    check(
        f"{variant['name']} selection fill vs Window {NON_TEXT_FLOOR}:1",
        contrast(selection, window) >= NON_TEXT_FLOOR - EPS,
        f"{contrast(selection, window):.2f}",
    )

    # Focus must stay the stronger of the two accents, as design.md promises.
    # On a dark scheme that means the higher ratio; on a light scheme too, since
    # contrast is what makes an outline readable either way.
    focus = contrast(rgb(scheme["Colors:Window"]["DecorationFocus"]), window)
    hover = contrast(rgb(scheme["Colors:Window"]["DecorationHover"]), window)
    check(f"{variant['name']} focus stronger than hover", focus > hover, f"focus {focus:.2f} > hover {hover:.2f}")


def audit_copies(variant: dict) -> None:
    """Every palette copy of a variant must be the scheme itself, byte for byte."""
    scheme = (ROOT / variant["scheme"]).read_bytes()
    copies = [
        ROOT / variant["style"] / "colors",
        ROOT / variant["laf"] / "contents" / "colors",
    ]
    for copy in copies:
        rel = copy.relative_to(ROOT)
        check(
            f"{variant['name']} palette copy {rel}",
            copy.exists() and copy.read_bytes() == scheme,
            "" if copy.exists() else "missing",
        )


def audit_metadata(variant: dict) -> str:
    """Checks package ids and links; returns the style package version."""
    name = variant["name"]
    style_dir = ROOT / variant["style"]
    metadata = json.loads((style_dir / "metadata.json").read_text(encoding="utf-8"))
    plugin = metadata["KPlugin"]
    version = plugin["Version"]
    check(f"{name} style id", plugin["Id"] == variant["style_id"], plugin["Id"])
    check(f"{name} style API", metadata.get("X-Plasma-API") == "5.0", str(metadata.get("X-Plasma-API")))

    scheme = config(ROOT / variant["scheme"])
    scheme_key = scheme["General"]["ColorScheme"]
    check(f"{name} scheme name", scheme_key == Path(variant["scheme"]).stem, scheme_key)

    laf_dir = ROOT / variant["laf"]
    laf = json.loads((laf_dir / "metadata.json").read_text(encoding="utf-8"))
    expected_id = f"com.mayanktaker.{variant['style_id']}.desktop"
    check(f"{name} look-and-feel id", laf["KPlugin"]["Id"] == expected_id, laf["KPlugin"]["Id"])
    check(f"{name} look-and-feel structure", laf.get("KPackageStructure") == "Plasma/LookAndFeel",
          str(laf.get("KPackageStructure")))
    check(f"{name} look-and-feel version", laf["KPlugin"]["Version"] == version,
          f"{laf['KPlugin']['Version']} vs {version}")

    defaults = config(laf_dir / "contents" / "defaults")
    check(f"{name} LAF selects the scheme", defaults["kdeglobals][General"]["ColorScheme"] == scheme_key,
          defaults["kdeglobals][General"]["ColorScheme"])
    check(f"{name} LAF selects the style", defaults["plasmarc][Theme"]["name"] == variant["style_id"],
          defaults["plasmarc][Theme"]["name"])
    # Derive from the package directory: display names may contain spaces.
    decoration_id = aurorae_id(variant)
    decoration = defaults["kwinrc][org.kde.kdecoration2"]["theme"]
    check(f"{name} LAF selects its decoration", decoration == f"__aurorae__svg__{decoration_id}", decoration)
    check(f"{name} LAF selects the widget style", defaults["kdeglobals][KDE"]["widgetStyle"] == "MTNightshift",
          defaults["kdeglobals][KDE"]["widgetStyle"])

    aurorae = ROOT / variant["aurorae"]
    entry = config(aurorae / "metadata.desktop")["Desktop Entry"]
    check(f"{name} decoration name", entry["X-KDE-PluginInfo-Name"] == decoration_id,
          entry["X-KDE-PluginInfo-Name"])
    check(f"{name} decoration version", entry["X-KDE-PluginInfo-Version"] == version,
          f"{entry['X-KDE-PluginInfo-Version']} vs {version}")
    return version


def plugin_version() -> str:
    """Reads the Qt style project version; it must equal the package version."""
    text = (ROOT / "application-style" / "CMakeLists.txt").read_text(encoding="utf-8")
    match = re.search(r"project\(\s*mtnightshiftstyle\s+VERSION\s+([0-9][0-9.]*)", text)
    check("Qt style project version declared", match is not None, "project() VERSION missing")
    return match.group(1) if match else ""


def audit_decoration(variant: dict) -> None:
    """The `.rc` padding and border are what KWin caches; they must match the artwork."""
    spec = importlib.util.spec_from_file_location(
        "build_decoration", ROOT / "tools" / "decoration-probe" / "build-decoration.py")
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)  # type: ignore[union-attr]
    params = generator.PARAMS
    rc = config(ROOT / variant["aurorae"] / f"{aurorae_id(variant)}rc")
    for key in ("PaddingTop", "PaddingBottom", "PaddingLeft", "PaddingRight"):
        check(f"{variant['name']} decoration {key}", int(rc["Layout"][key]) == params["padding"],
              f"{rc['Layout'][key]} vs {params['padding']}")
    for key in ("BorderLeft", "BorderRight", "BorderBottom"):
        check(f"{variant['name']} decoration {key}", int(rc["Layout"][key]) == params["border"],
              f"{rc['Layout'][key]} vs {params['border']}")


def main() -> int:
    """Runs every audit and reports the summary."""
    global QUIET
    QUIET = "--quiet" in sys.argv[1:]
    versions = set()
    for variant in VARIANTS:
        if not QUIET:
            print(f"{variant['name']}:")
        audit_copies(variant)
        versions.add(audit_metadata(variant))
        audit_palette(variant)
        audit_decoration(variant)
    check("one version across every package", len(versions) == 1, ", ".join(sorted(versions)))
    if len(versions) == 1:
        package_version = next(iter(versions))
        check("Qt style version matches packages", plugin_version() == package_version,
              f"{plugin_version() or 'missing'} vs {package_version}")

    if FAILURES:
        print(f"\n{len(FAILURES)} check(s) failed")
        return 1
    if QUIET:
        print(f"theme audit ok  {CHECKS} checks, one version {', '.join(sorted(versions))}")
    else:
        print("\ntheme audit passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
