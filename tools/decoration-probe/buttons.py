#!/usr/bin/env python3
# © Mayanktaker Computers & Web Development | https://mayanktaker.com
# SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development
# SPDX-License-Identifier: LGPL-2.0-or-later
"""Generate the five Aurorae button SVGs: fixed geometry, per-variant tones."""

from __future__ import annotations


def button_state(element_id: str, glyph: str, ring: str | None = None,
                 disc: str | None = None) -> str:
    """One button state group: optional 19px hover ring, optional 20px disc."""
    rows = [f'  <g id="{element_id}">',
            '  <rect x="0" y="0" width="24" height="24" fill="none" stroke="none"/>']
    if ring:
        rows.append(f'  <rect x="2.5" y="2.5" width="19" height="19" rx="6" fill="none" '
                    f'stroke="{ring}" stroke-width="1"/>')
    if disc:
        rows.append(f'  <rect x="2" y="2" width="20" height="20" rx="6" fill="{disc}"/>')
    rows.append("  " + glyph)
    rows.append("  </g>")
    return "\n".join(rows)


# Glyph geometry, byte-for-byte the original artwork; {tone} is the only variable.
BUTTON_GLYPHS = {
    "close": '<path d="M 8,8 L 16,16 M 16,8 L 8,16" fill="none" stroke="{tone}" '
             'stroke-linecap="round" stroke-linejoin="round" stroke-width="1.6"/>',
    "minimize": '<path d="M 8,12.5 L 16,12.5" fill="none" stroke="{tone}" '
                'stroke-linecap="round" stroke-linejoin="round" stroke-width="1.6"/>',
    "maximize": '<rect x="8" y="8" width="8" height="8" rx="1.5" fill="none" stroke="{tone}" '
                'stroke-linecap="round" stroke-linejoin="round" stroke-width="1.6"/>',
    "restore": '<rect x="7.5" y="9.5" width="7" height="7" rx="1.2" fill="none" stroke="{tone}" '
               'stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"/>'
               '<path d="M 10.5,7.5 H 15.5 Q 16.5,7.5 16.5,8.5 V 13.5" fill="none" stroke="{tone}" '
               'stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"/>',
    "menu": '<path d="M 8,8.5 L 16,8.5 M 8,12.5 L 16,12.5 M 8,16.5 L 16,16.5" fill="none" '
            'stroke="{tone}" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.6"/>',
}

BUTTON_LABELS = {
    "close": "close",
    "minimize": "minimize",
    "maximize": "maximize",
    "restore": "restore",
    "menu": "window menu",
}

BUTTON_NOTES = {
    "menu": '\n  KWin\'s default left button group is "MSE"; without this file the window'
            "\n  menu button falls back to the full-colour application icon.",
}

BUTTON_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!--
  {title} Aurorae {label} button.
  © 2026 Mayanktaker Computers & Web Development | https://mayanktaker.com
  SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development
  SPDX-License-Identifier: LGPL-2.0-or-later

  GENERATED FILE — edit tools/decoration-probe/buttons.py instead.
  Original artwork; 24x24 button, 20x20 state disc.{note}
-->
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" version="1.1">
  <title>{title} {label} button</title>
{states}
</svg>
"""


def build_buttons(palette: dict[str, str], title: str, blend,
                  deactivated_mix: float) -> dict[str, str]:
    """The five 24x24 button SVGs for one variant: fixed geometry, palette tones."""
    inactive = palette["foreground_inactive"]
    disabled_active = blend(palette["header_active"], inactive, deactivated_mix)
    disabled_inactive = blend(palette["header_inactive"], inactive, deactivated_mix)

    documents = {}
    for name, glyph in BUTTON_GLYPHS.items():
        states = [
            button_state("active-center", glyph.format(tone=palette["foreground"])),
            button_state("hover-center", glyph.format(tone=palette["negative"]),
                         ring=palette["negative"]),
            button_state("pressed-center", glyph.format(tone=palette["selection_text"]),
                         disc=palette["selection"]),
            button_state("deactivated-center", glyph.format(tone=disabled_active)),
            button_state("inactive-center", glyph.format(tone=inactive)),
            button_state("hover-inactive-center", glyph.format(tone=inactive), ring=inactive),
            button_state("pressed-inactive-center", glyph.format(tone=palette["selection_text"]),
                         disc=palette["selection"]),
            button_state("deactivated-inactive-center", glyph.format(tone=disabled_inactive)),
        ]
        documents[name] = BUTTON_TEMPLATE.format(
            title=title, label=BUTTON_LABELS[name],
            note=BUTTON_NOTES.get(name, ""), states="\n".join(states))
    return documents
