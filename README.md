© Mayanktaker Computers & Web Development | https://mayanktaker.com

# MT Dark KDE

[![theme checks](https://github.com/Mayanktaker/MT-Nightshift-KDE/actions/workflows/checks.yml/badge.svg)](https://github.com/Mayanktaker/MT-Nightshift-KDE/actions/workflows/checks.yml)

A modern, sculptured evolution of KDE Breeze for KDE Plasma 6. Built around **Nightshift OLED** (near-black carbon surfaces, restrained steel-blue highlights, and deliberate, solid geometry instead of distracting blur or glossy 3D effects), this suite provides 5 cohesive palette variants, custom 10px rounded Aurorae window decorations, a dedicated C++ Qt Widgets application style plugin, and a matching 20-wallpaper abstract collection.

![MT Dark KDE Wallpaper Palette](docs/screenshots/preview-wallpapers.png)

---

## Features

- **5 Hand-Crafted Variants**: Seamlessly switch between Nightshift (OLED carbon), Dayshift (crisp light), Nord Night (Polar Night slate), Nord Day (Snow Storm), and One Dark Pro (vibrant dark).
- **10px Rounded Window Decorations**: Aurorae theme generated with clean 10px rounded corners that match the control radius, continuous shadow envelopes, and 5 distinct window title bar buttons (close, minimize, maximize, keep-above, help) color-matched to each look.
- **C++ Qt Widgets Style Plugin (`MTNightshift`)**:
  - Shared 10px maximum radius for Qt control and interaction surfaces, including fields, buttons, tabs, indicators, menu rows, item hovers **and the outer window corners**; QMenu popup corners stay 15px as the popup tier.
  - Rounded list and sidebar delegate backgrounds in QQC2 Desktop Style applications, including Discover, through `PE_PanelItemViewRow` and `CE_ItemViewItem`.
  - Borderless, rounded path bar in Dolphin (`KUrlNavigator`) with focus ring.
  - Slim 12px scrollbar gutters across all Qt applications with clean sidebar gutter suppression in Dolphin.
- **Plasma 6 Desktop Theme & Popups**: Breeze's 6px panel and dialog frames, a 14px popup frame (`widgets/background`), and high-contrast widget styling. Kirigami-owned popup/menu corner radii remain KDE-controlled.
- **20 Palette-Matched Abstract Wallpapers**: High-definition, text-free abstract wallpapers for all 5 variants across 16:9 Full HD (`1920x1080`), 32:9 Dual-FHD (`3840x1080`), 32:9 Dual-QHD (`5120x1440`), and 16:9 4K UHD (`3840x2160`).
- **Rigorous Contrast & Accessibility Standards**: All variants enforce WCAG AA text contrast floors (minimum 4.66:1) and strong UI element contrast (minimum 3.0:1) verified via automated testing.

---

## The Five Variants

| Variant | Style | Dominant | Deep / Lightest | Mid Surface | Accent | Highlight |
|---|---|---|---|---|---|---|
| **Nightshift** | Dark (OLED) | `#101216` | `#0A0B0D` | `#1B1F25` | `#1F6E9C` | `#4FB4E6` |
| **Dayshift** | Light | `#EFF1F5` | `#FAFBFD` | `#F4F6F9` | `#1F6E9C` | `#256D9F` |
| **Nord Night** | Dark (Slate) | `#2E3440` | `#232932` | `#3B4252` | `#84A5C6` | `#A9CEE0` |
| **Nord Day** | Light (Cool) | `#ECEFF4` | `#F7F9FC` | `#E5E9F0` | `#4C6B91` | `#1F5F8C` |
| **One Dark Pro** | Dark | `#282C34` | `#1D1F23` | `#404754` | `#528BFF` | `#7FBEF2` |

---

## Installation

See **[INSTALL.md](INSTALL.md)** for prerequisites, the one-command install, per-variant
selection, manual installation, the plugin build, uninstall targets and troubleshooting.

```bash
make apply VARIANT=nightshift   # install all five variants and select one
make verify-live VARIANT=nightshift
make uninstall                  # user-local packages
make style-uninstall            # the system plugin (sudo)
```

## Desktop Wallpapers

The `Wallpapers/` directory contains 20 minimal, text-free abstract wallpapers specifically composed and color-matched for each theme variant:

- **16:9 Full HD (`1920x1080`)**: Perfect for standard displays (`nightshift-abstract-1920x1080.png`, etc.)
- **32:9 Panoramic Dual-FHD (`3840x1080`)**: Ideal for dual-1080p monitor spans
- **32:9 Panoramic Dual-QHD (`5120x1440`)**: High-res panoramic edition for dual-1440p monitors
- **16:9 4K UHD (`3840x2160`)**: Ultra-high definition 4K edition

### Setting a Wallpaper

Global themes in this repository deliberately omit wallpaper defaults to preserve user customization. Apply any wallpaper from the terminal:

```bash
plasma-apply-wallpaperimage Wallpapers/nightshift-abstract-1920x1080.png
```

Or for dual-monitor setups:
```bash
plasma-apply-wallpaperimage Wallpapers/nightshift-abstract-3840x1080.png
```

See [`Wallpapers/README.md`](Wallpapers/README.md) for master prompts, palette blocks, and regeneration instructions.

---

## Quality Assurance & Verification

This project features a comprehensive offscreen testing suite:

```bash
# Run all automated tests
make check
```

What `make check` asserts:
- **Aurorae Invariants**: Verifies continuous shadow ramps, lack of corner cutouts, and 10px border geometry across all variants (`tools/decoration-probe/check-decoration.py`).
- **Button Palette Audit**: Proves all 5 buttons and 8 interaction states match each variant's color scheme (`tools/decoration-probe/check-buttons.py`).
- **Package Integrity & Contrast**: Confirms byte-identical palette copies across packages and verifies that all 64 text/surface pairs meet or exceed the 4.66:1 contrast floor (`tools/theme-audit/check-theme.py`).
- **Wallpapers Verification**: Validates file presence, exact target dimensions, and PNG optimization (`tools/wallpapers/build-wallpapers.py --check`).
- **Qt Style Probe**: Offscreen Qt probe rendering test widgets through the built plugin and asserting shared 10px control / 15px popup tapers, hover and 1px focus outlines, on-pill label contrast for tabs, the tonal checked tool button with its icon at 3:1, tab idle/hover steps, the inset menu separator, split-ink meter labels at 0% and partial fill, and 12px scrollbar gutters (`tools/style-probe/check-style.py`).
- **Shipped Frame Geometry**: Reads the top-left corner path of the panel, dialog and popup frames in every variant and asserts 6px / 6px / 14px, so the artwork cannot drift from the documentation.
- **Colour Maths**: Unit checks for blending, contrast and palette-group selection, including the out-of-range inputs the image probe cannot reach (`tools/style-probe/check-math.cpp`).
- **Look-and-Feel Packages**: Installs each of the five packages into a temporary `XDG_DATA_HOME` with `kpackagetool6`; the check prints an explicit skip when the tool is unavailable.
- **Release Installer**: Every generated `install.sh` is syntax-checked and executed in a throwaway home with a stub `kpackagetool6` before the archive is written.

To verify that your currently running session matches the active theme:
```bash
make verify-live VARIANT=nightshift
```

### Live desktop confirmation

Automated checks cover artwork, contrast, package metadata, and Qt offscreen rendering. A final manual pass should also verify:

- Right-click panel menus and tooltips on a dark wallpaper and a genuinely light wallpaper.
- Dolphin's editable path bar focus ring after opening the editable location field.
- Nord Night alternate selected rows without a custom `[General] AccentColor`.
- Restore the active `[KDE] frameContrast`, scheme, Plasma Style, decoration, wallpaper, and panel settings after testing.

The exact expected result for each of these is written down in
[`validation.md`](validation.md) §"Live spot-checks", together with the measured reason they
are not automated (pointer injection drifts by several pixels, and injected keystrokes do not
reach focused clients).

Release package archives are accompanied by `dist/SHA256SUMS`; verify both the archive and the digest before installation.

---

## Project Structure

```
├── application-style/       # C++ Qt Widgets style plugin (source, kstyle themerc)
├── color-schemes/           # Master KDE color schemes (.colors)
├── docs/                    # Screenshot previews and archived design notes
├── INSTALL.md               # Prerequisites, install, plugin build, release procedure
├── design.md                # Shared design language (palette, shape, states)
├── decoration.md            # Aurorae window decoration spec
├── application-style.md     # Qt Widgets style spec
├── variants.md              # Dayshift and One Dark Pro notes
├── validation.md            # What each check measures, and what it cannot see
├── CHANGELOG.md             # User-visible changes per release
├── themes/
│   ├── aurorae/             # Aurorae window decorations (MTNightshift, MTDayshift, ...)
│   ├── mt-*-global/         # Plasma Look-and-Feel metadata packages
│   └── mt-*/                # Plasma desktop theme assets (widgets, dialogs)
├── tools/
│   ├── decoration-probe/    # Aurorae SVG generator, probe, and button validator
│   ├── packaging/           # KDE Store and release tarball packaging tooling
│   ├── plasma-theme/        # Plasma dialog and applet frame generators
│   ├── style-probe/         # Offscreen Qt Widgets tester and colour-math checks
│   ├── theme-audit/         # Contrast and package metadata auditor
│   └── wallpapers/          # Wallpaper build and verification tooling
├── upstream/                # Upstream KDE Breeze 6.8.2 reference baseline
└── Wallpapers/              # 20 palette-matched wallpapers and lossless sources
```

---

## Attribution & Licensing

- Upstream theme assets and baseline are derived from [KDE Breeze](https://invent.kde.org/plasma/breeze) and [libplasma](https://invent.kde.org/plasma/libplasma) (KDE Visual Design Group). Upstream notices and per-file licenses are strictly preserved under `upstream/` and [`LICENSES/`](LICENSES/).
- Original code and artwork marked `LGPL-2.0-or-later` are covered by [`LICENSES/LGPL-2.0.txt`](LICENSES/LGPL-2.0.txt).
- The **One Dark Pro** palette is derived from Binaryify's [One Dark Pro](https://github.com/Binaryify/OneDark-Pro) (MIT, Copyright (c) 2013-2022 Binaryify); see [`LICENSES/MIT.txt`](LICENSES/MIT.txt).
- This project does not claim KDE authorship or imply KDE endorsement.
