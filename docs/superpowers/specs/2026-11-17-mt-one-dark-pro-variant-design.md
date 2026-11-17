© Mayanktaker Computers & Web Development | https://mayanktaker.com

# MT One Dark Pro — fifth KDE theme variant

## Intent and why

Add one dark theme variant that carries the recognised One Dark Pro identity onto this
desktop: the user pointed at One Dark Pro's own documentation and chose a full fifth
variant over a scheme-only or retro-fit option. The four existing variants stay exactly
as they are; this is a new palette identity on the same generated geometry and the same
palette-driven Qt plugin. No light counterpart is in scope.

## Goals

- One full variant: color scheme, Plasma Style, Look-and-Feel and Aurorae decoration,
  registered beside the existing four and installable with `VARIANT=one-dark-pro`.
- The standard One Dark Pro palette (`oneDarkPro.ts`, not Flat or Mix) is the source of
  truth; only tones the audit rejects are lifted, with each change recorded.
- MIT provenance is explicit: license text, copyright notice and a README pointer.
- All five variants remain under one generator, one audit, one style probe and one
  apply/verify-live table.

## Non-goals

- No changes to Nightshift, Dayshift, Nord Night or Nord Day palettes or packages.
- No light/One Light counterpart.
- No new Qt plugin, no new SVG geometry, no decoration generator redesign.

## Anti-goals

- Renaming or retuning an existing variant into One Dark Pro.
- Copying upstream VS Code JSON into the repo and calling that a theme; the scheme must
  follow this project's group layout and audit floors.
- Claiming the derived artwork is by Binaryify or implying endorsement.

## Constraints

- `check-theme.py` enforces one version across all packages: every new package reports
  **1.6.0**; the plugin stays at its current version.
- Text floor **4.66:1**, non-text floor **3:1**, focus stronger than hover.
- All palette copies (scheme, style, LAF) are byte-identical, including the credit header.
- Decoration and the five buttons are generated, never hand-edited; `--check` covers all
  five variants.
- One Dark Pro is MIT licensed (`LICENSE.txt`: Copyright (c) 2013-2022 Binaryify). The
  notice and permission text must travel with the derived palette.

## Approaches

- **A. Full fifth variant (chosen).** Add one registered variant with all four packages,
  generated artwork and an MIT attribution trail. Shares every generator; costs one
  palette to tune and one live pass.
- **B. Colour scheme only.** Cheaper but no decoration or Look-and-Feel identity;
  rejected by the user's choice.
- **C. Retune Nightshift.** Destroys an existing shipped identity; rejected.

## Design

### Naming

| Item | Value |
|---|---|
| Scheme | `color-schemes/MT-One-Dark-Pro.colors` |
| Plasma Style | `themes/mt-one-dark-pro/` |
| Look-and-Feel | `themes/mt-one-dark-pro-global/` |
| LAF id | `com.mayanktaker.mt-one-dark-pro.desktop` |
| Aurorae | `themes/aurorae/MTOneDarkPro/` |
| Decoration id | `__aurorae__svg__MTOneDarkPro` |
| Style id | `mt-one-dark-pro` |

All packages at **1.6.0**; widget style key stays `MTNightshift`.

### Palette mapping (computed first pass; the audit is the source of truth)

Upstream tokens: editor `#282c34`, sidebar `#21252b`, input `#1d1f23`, panel `#404754`,
editor foreground `#abb2bf`, activity-bar foreground `#d7dae0`, title inactive
`#6b717d`, link `#61afef`, caret `#528bff`, badge `#4d78cc`, warn `#d19a66`, ANSI red
`#e05561`, green `#8cc265`, magenta `#c162de`.

| Role | Value | Derivation / reason |
|---|---|---|
| Window, Header active | `#282c34` | editor / title bar background verbatim |
| View / Base | `#1d1f23` | input background verbatim |
| Complementary, Header inactive | `#21252b` | sidebar / status background; gives inactive fill a real step |
| Button / alternate | `#404754` / `#30333d` | button background / secondary background verbatim |
| Tooltip / alternate | `#21252b` / `#2c313a` | hover widget / list active selection |
| Text | `#d7dae0` | activity-bar foreground; clears 4.66:1 even on the button tone |
| Inactive text | `#9da5b4` | title active foreground lifted from upstream `#6b717d` (2.86:1) |
| Focus / hover | `#61afef` / `#528bff` | link and caret tones; focus 5.92:1 > hover 4.33:1 on Window |
| Selection / alternate | `#528bff` / `#61afef` | with Base `#1d1f23` text (5.10:1 / 6.98:1) |
| Negative | `#f07b86` | lifted from ANSI red `#e05561` (3.76:1) |
| Neutral / Positive / Link | `#d19a66` / `#8cc265` / `#61afef` | upstream warn / ANSI green / link, all pass |
| Visited | `#cf7ce7` | lifted from ANSI magenta `#c162de` (4.05:1) |

The frame line is an explicit per-variant token derived from the header and foreground,
as for the other four. Only values the audit rejects change from the table above; record
each final value and its measured floor in `validation.md`.

### Provenance and files to touch

- `LICENSES/MIT.txt` — the upstream MIT text, with the 2013-2022 Binaryify notice.
- `LICENSES/README.md`, `README.md` — one pointer each stating that the One Dark Pro
  palette is derived from upstream, MIT terms travel with it, and the KDE/LGPL boundary
  is unchanged.
- `color-schemes/MT-One-Dark-Pro.colors` and the three palette copies in the new style
  and LAF: all four carry the same `SPDX-FileCopyrightText: 2013-2022 Binaryify` line and
  a pointer to `LICENSES/MIT.txt`, while keeping the existing KDE contributor notices.
- `tools/theme-audit/check-theme.py`, `tools/decoration-probe/build-decoration.py`,
  `tools/style-probe/check-style.py`, `Makefile` — one new entry each; no new logic.
- `themes/aurorae/MTOneDarkPro/` — decoration and five buttons generated with
  `--variant one-dark-pro`; `.rc` keeps padding 32 / border 6.
- `AGENTS.md`, `design.md`, `validation.md`, `PLAN.md`, `plan-archive.md` — pointers,
  final measurements and live evidence.

### Verification

`make check` and `make check-dpr2` across all five variants, five offscreen style
renders, then `make verify-live VARIANT=one-dark-pro`, a live capture on both wallpaper
types, and restore to the previously active variant. Confirm the MIT notice appears in
all four palette copies and in `LICENSES/`.

## What's left to the builder

Exact lifted tones are settled by the audit, not by this document. Live screenshots are
the acceptance evidence. This Wayland session has no pointer injection; use the recorded
DBus/Spectacle recipe in `AGENTS.md`.
