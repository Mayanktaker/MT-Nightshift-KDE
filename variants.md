# MT Nightshift — palette variants

© Mayanktaker Computers & Web Development | https://mayanktaker.com

The suite ships five palettes over one geometry and one palette-driven plugin.
[`design.md`](design.md) defines the shared design language (§1–§11); Nightshift is
the reference palette in §2. This file records what changes when the palette is
light instead of dark, and what the two imported/reconstructed palettes needed
beyond a straight retone.

## 1. MT Dayshift — the light counterpart

Dayshift is the light sibling of Nightshift, the way Breeze pairs with Breeze Dark: identical geometry and shape language, inverted surface tones. `color-schemes/MT-Dayshift.colors` carries cool carbon-whites (Window `239,241,245`, Base `250,251,253`, Button `244,246,249`, Header `243,245,248`) with the same restrained Breeze-blue accents and the shared Selection group; list alternation stays unified with the row background per `application-style.md`. Semantic colours are re-tuned for light surfaces rather than reused: every `Foreground*` role clears 4.66:1 against both backgrounds of its group there too, so Active is `#256D9F`, Link `#1F6AAE`, Visited `#7358AD`, Negative `#AB484D`, Neutral `#8E5D10`, Positive `#1B7740`, and the dimmed inactive header keeps its own pair (`#1F5E89` active, `#616873` inactive, `#5C636C` normal). The accent pair inverts with the surface, because on light contrast means *darker*: focus is `#2A7FA8` (3.95:1 on `Window`) and hover is the quieter `#2E8DBE` (3.28:1) — the same "hover quiet, focus unmistakable" rule as `design.md` §2, with the strengths swapped because the background did. Breeze's list artwork still paints the selected-row pill from the focus token at 80%, which composites to `#5498B9` over a light row; the theme's dark text clears 5.2:1 on it. Packages mirror the dark set: `themes/mt-dayshift/` (Plasma Style, same palette-driven SVG assets — including the 14px popup frame), `themes/mt-dayshift-global/` (Look-and-Feel selecting the Dayshift scheme, style and decoration), and `themes/aurorae/MTDayshift/` (decoration generated from the same `PARAMS` geometry with the light palette through `build-decoration.py --variant dayshift`; button geometry is shared with Nightshift and button tones are generated per variant). The application style plugin is palette-driven and needs no variant: the same `MTNightshift` style draws its pill surfaces from whichever scheme is active. `make apply` installs all five variants and keeps Nightshift selected; `make apply-dayshift` selects the light one, `make apply VARIANT=nord-night` / `VARIANT=nord-day` select the Nord pair, and `make apply VARIANT=one-dark-pro` selects the fifth (§2 of this file).

Nord Night and Nord Day are the second pair: the same geometry, generated
decoration and palette-driven Qt style, with the canonical Nord Polar Night /
Snow Storm surfaces, Frost accents and Aurora semantics adjusted only where the
audit forced a tone to move (§"Measured floors" in `validation.md`). Nord Night
is a dark, blue-grey sibling of Nightshift (Window `#2E3440`, active header
`#3B4252`), Nord Day a light, cool sibling of Dayshift (Window `#ECEFF4`, active
header `#E5E9F0`). The inactive header inverts the active pair in both, and
their pressed button pill is `Selection` from the scheme — light `#84A5C6` on
Nord Night with dark `#2E3440` glyphs, deeper `#4C6B91` on Nord Day with white
glyphs (`decoration.md` §2). Both were applied and verified live on 2026-11-16 on the light
and dark wallpaper regions; `plan-archive.md` holds the captures and
measurements.

Frame geometry is measured on the files that actually ship. The panel (`widgets/panel-background.svgz`) and dialog (`dialogs/background.svgz`) frames keep Breeze's 6px band; the popup frame (`widgets/background.svgz`) is the 14px surface that `tools/plasma-theme/applet-background.py` generates through `round-panel-corners.py`. `check-style.py` reads the top-left corner path of all three assets in every variant and asserts 6/6/14px, so the artwork and this section cannot drift apart again. KSvg (Plasma 6.8) derives border sizes from the slice elements' sizes and content margins from the hint rects' sizes; a corner smaller than its border gets stretched into a distorted arc.
Item-view highlights are ours as well: `PE_PanelItemViewItem` and `PE_PanelItemViewRow` paint 10px-radius inset pills (4px side insets) for every list, tree and icon view — including QQC2 Desktop Style rows in Kirigami apps — while selections take `Highlight` while the window is active and a muted grey when inactive, hovers a faint tone step, and idle items paint nothing so views keep their own backgrounds. This upgrades the System Settings sidebar, Dolphin's Places panel, Discover-style delegate rows, icon-view selections and KDE text lists from square full-width bands to the shared control language.
Progress meters are ours too: KCapacityBar has no KStyle under a QProxyStyle, so it falls back to `CE_ProgressBar` — Breeze's groove paints in near-black `Base`, which read as a black slab in Dolphin's free-space meter. The style owns determinate horizontal `CE_ProgressBar` draws with a shared 10px maximum radius, subtle `Window`→`Base` groove, `Highlight` fill and inline text, while busy indicators keep Breeze's animation. Narrow fills use a proportionally smaller corner so short progress remains a rounded bar instead of a circular dot. KCapacityBar's own "eye" QPainter fallback — the actual black-blob source — is bypassed by declaring `Q_CLASSINFO("X-KDE-CustomElements")` and answering KDE's custom-element query (`styleHint 0xff000001`, element name in the widget's `objectName`) with our own element id, which `drawControl` maps to the same surface. Disabled fields keep their shape instead of vanishing: `paintFieldSurface` gives the whole disabled family (Base-tone edits, editable-combo and Button-tone combos alike) one lifted tone plus a dimmed hairline, because greyed-out settings pages — the Login Screen KCM greys out every combo — otherwise render Base-tone editors darker than the page and Button-tone ones nearly indistinguishable from it. The step is mixed from the *enabled* `Window`/`WindowText` pair, so it points away from the surface in both directions — a lift on the night variants (`#202226`, 1.18:1 over `Window`), a recess on the day variants (`#DFE1E5`, 1.16:1) — with the hairline one 1px dim tone inside the shape (1.33:1 and 1.22:1 against the fill). Mixing the two muted disabled tones instead (the first implementation) collapsed on light: Dayshift's `Window` and `Button` differ by 5/255, so the field measured a 1.01:1 step against the page and read as one flat block. Getting there also fixed a guard-order bug: a frameless combo/spin child editor exited `paintLineEdit` at the frameless guard and let Breeze stamp its square `Base` fill over the container's surface before the combo-child guard could suppress it; the combo-child guard now runs first.
Devices capacity bars in the Places sidebar are raw `QPainter` inside KIO and cannot be styled; their warning fill follows the scheme's `ForegroundNegative`, softened from the pastel `234,113,124` to the muted crimson `208,128,132` (`#D08084`, in all three copies of the scheme), which also calms error text globally. That dimming had overshot: the first shipped value `206,112,116` measured 4.07:1 on the `Button` alternate, below AA, so `tools/theme-audit/check-theme.py` now measures the floor on every run. The remaining edge language was dimmed in the same pass: `[KDE] frameContrast` 0.14 → 0.05 (client hairlines — the status strip separator, toolbar line and sidebar seams are now whispers; area tone steps keep the boundaries legible) and the decoration's `frame_line_contrast` 0.20 → 0.06 (window outer frame line and corner arc), both re-verified by `make check`/`make check-dpr2` after regenerating `decoration.svg`.
The field family was completed after live screenshots exposed Breeze's default radius leaking through: the file dialog's location combo (`KUrlComboBox`, editable) and its `Name` field rendered with Breeze's small frame, and clicking Dolphin's path bar swapped the breadcrumb pill for the same default-rounded edit. The latest pass puts those controls and their hover/focus outlines on the same 10px radius as menu and item interactions, without changing QMenu, shell-popup or window outer corners. The offscreen probe (`tools/style-probe/render-fields.cpp`) renders resting, hover, forced-focus, symbol-mode and step-limit states, and checks short meter fills and corner tapers across all five schemes; `make check` renders through the built plugin on every run (CI included, Qt minimum relaxed to 6.4 for the ubuntu image, Breeze-dependent assertions skipped there), and the scrollbar gutter assertion doubles as the 12px visual check outside Dolphin.

Scrollbars keep Breeze painting and interaction behavior. `PM_ScrollBarExtent` caps their gutter at 12 logical pixels, preserving Breeze's 8px handle. In Dolphin only, the scrollbar owned by the public KIO `KFilePlacesView` in the main window gets a 0px extent, removing its gutter; dialog-hosted Places views retain the slim scrollbar. Detection uses the application name and Qt meta-object class name without linking Dolphin/KIO internals. Overflow in that panel has no visible scrollbar cue, but wheel, keyboard and touch scrolling remain available. The updated plugin is installed; offscreen Qt tests confirm 0px for the Dolphin Places view, 12px for other views and Dolphin dialogs, and wheel scrolling with a long list while the bar has zero width. A fresh Dolphin screenshot confirms the sidebar has no scrollbar; live keyboard/touch testing in Dolphin remains outstanding.

KDE's Qt platform theme prefers the complete `[Colors:*]` groups in `kdeglobals` over the `General/ColorScheme` fallback. An accent-color update can leave partial groups that omit `BackgroundNormal`; KColorScheme then supplies Breeze Light's white default even though `ColorScheme=MT-Nightshift`. If a fresh Qt app reports `QPalette::Base=#ffffff`, switch to another scheme and reapply MT Nightshift so Plasma rewrites the complete palette groups. Verify `Colors:View/BackgroundNormal=10,11,13` and `Colors:Window/BackgroundNormal=16,18,22`.

## 2. MT One Dark Pro — the fifth variant

One Dark Pro is a dark, blue-accented look carried over from Binaryify's
[One Dark Pro](https://github.com/Binaryify/OneDark-Pro) (MIT, Copyright (c)
2013-2022 Binaryify). It is a new palette on the same generated geometry and the
same palette-driven `MTNightshift` plugin — no new artwork construction, no new
plugin and no light counterpart. All four packages report 1.6.0:
`color-schemes/MT-One-Dark-Pro.colors`, `themes/mt-one-dark-pro/`
(Plasma Style), `themes/mt-one-dark-pro-global/` (Look-and-Feel
`com.mayanktaker.mt-one-dark-pro.desktop`) and
`themes/aurorae/MTOneDarkPro/` (decoration `__aurorae__svg__MTOneDarkPro`). It is
selected with `make apply VARIANT=one-dark-pro` and checked with
`make verify-live VARIANT=one-dark-pro`.

The palette follows the standard `oneDarkPro.ts` tokens (not Flat or Mix):
editor `#282C34` for Window and the active header, input `#1D1F23` for the View
Base, sidebar `#21252B` for the complementary and inactive-header surface,
button `#404754`, link `#61AFEF` for focus and caret `#528BFF` for selection.
Body text is the activity-bar foreground `#D7DAE0`. The audit rejected seven of
the first-pass muted tones on the relatively light `#404754` button face and
each was lifted the minimum that clears the floor while keeping its hue; the
seven lifts, the final 4.67 text floor and the measured focus/hover/selection
ratios are recorded in `validation.md` §"One Dark Pro lifts". The frame line is
an explicit per-variant `#32363E` token (`decoration.md` §2), and the decoration buttons carry a `#528BFF`
pressed pill with dark `#1D1F23` glyphs.

The provenance trail is `LICENSES/MIT.txt` (the verbatim upstream `LICENSE.txt`)
plus one pointer each in `LICENSES/README.md` and `README.md`. The three
byte-identical palette copies carry the Binaryify SPDX line alongside the KDE
contributor notices. The KDE/LGPL boundary for the Breeze-derived Plasma assets
is untouched, and no Binaryify authorship or endorsement of the derived artwork
is implied.

The fifth variant was applied and verified live on 2026-11-17: the titlebar
buttons and 1px frame line stay legible on both a bright wallpaper
(`/tmp/opencode/one-dark-pro-light.png`) and the dark DarkestHour wallpaper
(`/tmp/opencode/one-dark-pro-dark.png`), and the session was returned to the
Nightshift baseline afterwards. `plan-archive.md` holds the evidence.
