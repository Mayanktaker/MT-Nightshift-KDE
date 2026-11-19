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

### Fixed

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
