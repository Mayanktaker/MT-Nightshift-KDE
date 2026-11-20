# Changelog

User-visible changes to the MT Nightshift theme set. The full history is in
`git log`; this file records what someone installing or updating the theme
needs to know.

## Unreleased

### Changed

- One 10px radius for Qt control surfaces and their hover, pressed and focus
  states — fields, buttons, tabs, chips, menu rows and item rows. QMenu windows
  keep their 15px outer radius, and window, panel and dialog frames are
  unchanged.
- Fields, combo boxes and spin boxes show a quiet accent outline on hover and
  the stronger 1px ring on keyboard focus.
- Check and radio chips use the Button tone with a quiet hairline; disabled
  chips step toward the page tone, and keyboard focus is drawn on the chip.
- Short progress and capacity fills stay rounded bars instead of collapsing into
  a circle.
- Check and radio marks keep a clear margin from the chip edge.
- App tooltips use the 10px control radius instead of 6px, so they are no longer
  the sharpest rectangle on screen.

### Tooling

- The dialog and popup frame generators now cover all five variants and their
  lookup slots (15 files each), so the three previously unguarded variants can no
  longer drift. Generated output is unchanged.
- The decoration generator's documented trial overrides (`--padding`, `--radius`,
  `--peak`, `--arc`) work; they previously produced identical output because the
  geometry was captured at import. The padding/radius guard now applies to
  overrides too.

### Fixed

- Selected tab labels and checked tool button labels now use on-pill ink. They
  measured 1.5–2.7:1 against the accent fill on One Dark Pro, Nord Day, Nord
  Night and Dayshift; every variant now clears 4.86:1.
- Tabs have a hover state again: hover is a 13% step over the 7% idle surface,
  and the selected tab keeps the accent fill. The previous single tone made idle
  and hovered identical.
- Pressed and checked tool buttons now take a tonal fill instead of the full
  accent. Their symbolic icons are pre-rendered by the icon theme and cannot be
  recoloured, so the saturated fill left them at 2.2–2.3:1 on three variants;
  text and icon now measure 4.7–9.9:1.
- Menu separators are inset, so they no longer cut across the menu's rounded
  corner.
- Progress labels stay readable on both the fill and the groove side.
- A disabled checked tool button no longer paints a full accent pill.
- Item-view focus rings no longer wrap non-list widget labels in a capsule.
- The colour-blend helper clamps its weight, so an out-of-range value can no
  longer produce an invalid colour that paints nothing.

### Tooling

- The Qt style sources are split into focused units, and the plugin version is
  asserted against the shipped packages.
- `make uninstall` removes the user-local packages; `make style-uninstall`
  removes the system plugin and its metadata.
- Every release installer is syntax-checked and executed in a throwaway home
  before it is archived.
- `make check` validates all Look-and-Feel packages with `kpackagetool6` when it
  is available and runs colour-math unit checks.
- CI runs the suite on Fedora 45 as well as Ubuntu; tagging `v*` publishes the
  archives and `SHA256SUMS` to a GitHub Release.
- The shipped frame corners are measured directly (6px panel and dialog, 14px
  popup) instead of a regenerated sample.

## 1.6.1

- Five palette variants: Nightshift, Dayshift, Nord Night, Nord Day and One Dark
  Pro, sharing one decoration geometry and one palette-driven Qt style.
- 20 matching abstract wallpapers across Full HD, dual-FHD, dual-QHD and 4K.
- KDE Store packages plus complete-suite tarballs with a `SHA256SUMS` manifest.
- Rounded Qt menus, tabs, status strips and item-view rows.
