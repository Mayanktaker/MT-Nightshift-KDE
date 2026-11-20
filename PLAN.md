© Mayanktaker Computers & Web Development | https://mayanktaker.com

# MT Dark KDE — modernization plan

Working list. Closed items and their evidence (measurements, captures, commands) live in
[`plan-archive.md`](plan-archive.md); they are moved there when they close so this file stays
the current state rather than the history.

## Steps

- [ ] In a hands-on desktop pass, open the panel context menu and a tooltip (the panel Opaque state and the launcher/widget-explorer popups were checked on 2026-11-16). `ydotool` now injects pointer events into this session, so clicks land, but two limits remain: the pointer is relative-only with several pixels of accumulated error (fine for "somewhere in this window", not for a specific applet), and injected key events reach KWin's global shortcuts but not focused clients (`Escape`, `Ctrl+L` and typed text are dropped), so keyboard-driven checks still need a hand.
- [ ] Click the editable path field once by hand to confirm the 10px accent ring around a Base fill (`Ctrl+L` cannot be injected; see the pointer/key limits above). Live Qt Widgets button geometry *is* now confirmed: the "Open with Kate" dialog on 2026-11-20 showed 10px corners, a 1px accent focus ring and clear icon/text inset. The editable field itself was verified live on 2026-11-16 (15px taper, `#0A0B0D` fill, no frame pixels) after Dolphin's "Editable Location" action; AT-SPI's `SetFocus`/`Press` actions did not focus `KUrlNavigator` on Wayland, so the ring remains unconfirmed live and is still asserted offscreen by `check-style.py`.
- [ ] In a session without a custom `[General] AccentColor`, confirm the lighter Nord Night selected alternate row live. This session's accent override (`33,98,138`) governs Qt's selection fill, so the `Selection.BackgroundAlternate` step (`#93B3D1` over `#84A5C6`) is proven by the palette audit and offscreen probe, not by a live pill; see `validation.md`.

## Five named variants (2026-11-17)

Five named looks are installed and selectable: `nightshift` (default), `dayshift`, `nord-night`, `nord-day` and `one-dark-pro`. `make apply VARIANT=<name>` selects one and `make verify-live VARIANT=<name>` checks it; `apply-dayshift`, `apply-nord-night`, `apply-nord-day` and `apply-one-dark-pro` are aliases. All theme packages are 1.6.1, the Qt style plugin is unchanged at 1.4.0, and the decoration's frame line and five buttons are generated from each variant's palette. Qt Widgets menus (including submenus), their hovered rows, hovered/pressed/checked tool buttons, and QQC2 Desktop Style list/sidebar delegate rows now use the same 15px surface language as the field family; Plasma QML popup/menu surfaces and the notification history remain KDE-controlled. The closed Nord, One Dark Pro and rounded-menu work, with its measurements and live capture paths, is in [`plan-archive.md`](plan-archive.md).

## Desktop Wallpapers (2026-11-17)

A complete 20-wallpaper abstract suite matching the exact palette blocks of all five looks is provided in `Wallpapers/` (Full HD 1920x1080, Dual-FHD 3840x1080 32:9, Dual-QHD 5120x1440 32:9, and 4K UHD 3840x2160). Managed by `tools/wallpapers/build-wallpapers.py` with lossless source masters under `Wallpapers/sources/`, rebuildable via `make wallpapers` and verified by `make check`. Detailed prompts, resolutions and provenance are documented in [`Wallpapers/README.md`](Wallpapers/README.md).

## Chosen direction

Nightshift OLED is the selected mockup: dark, calm, and high-contrast without turning every surface pure black. Keep Breeze's blue identity, but use it selectively for focus, selection, and active controls. Favor opaque, solid surfaces and deliberate edges over gradients, blur, and glow.


## Baseline and scope


The current baseline is the host's official Fedora KDE Plasma 6.8.2 assets: the complete shared `default/` Plasma Style asset folder, Breeze Dark's `breeze-dark/` metadata/palette, and the global `BreezeDark.colors` file. The Plasma Style inherits shared assets from `default/`; the copy is unmodified under `upstream/`.

This plan covers the Plasma desktop theme, global color scheme, Look-and-Feel manifest, Aurorae decoration and Qt Widgets style plugin. The style plugin is built against Qt 6.11.2 and wraps the installed Breeze style; it requires system plugin installation to appear in the selector and must be rebuilt after incompatible Qt updates. Cursors and other Breeze components are not replaced.

## Audit follow-up (2026-11-19)

Closed from the improvement table:

- One version: the Qt style project reports `1.6.1` and `check-theme.py` asserts it
  against the packages, so a plugin/package split cannot recur.
- The style source is split into `stylepainting`, `stylerecognition`, dispatch,
  controls, fields, items and indicators; no file carries the whole implementation.
- `make uninstall` and `make style-uninstall` close the lifecycle gap.
- Release installers are syntax-checked and executed in a throwaway home before
  archiving.
- `make check` validates all five Look-and-Feel packages with `kpackagetool6`, runs
  colour-math edge cases, and measures the shipped frame corners (panel 6px, dialog
  6px, popup 14px) instead of a regenerated sample. The panel/dialog documentation
  was corrected to match the shipped artwork; no outer geometry changed.
- CI gains a Fedora 45 job; tagging `v*` publishes the archives and `SHA256SUMS`.
- `CHANGELOG.md` records user-visible changes.

Still open: per-variant UI screenshots (five live apply/restart passes) and the
three pointer-dependent live checks listed above.

## Radius hierarchy (2026-11-20)

Closed: tooltips moved from the 6px tier to the 10px control tier, and both frame
generators now cover all five variants and their lookup slots (15 files each),
which previously left three variants unguarded. Generated assets are unchanged.

Open, with a stated reason rather than an oversight: **full-window dialogs and the
panel frame still ship Breeze's 6px band**, so containers there are sharper than
the 10px controls they hold. Raising them needs new 12px corner bodies, not a
slice resize, and both earlier attempts shipped visible defects (a chord across
the corner; a corner smaller than its border that KSvg stretched). The decision
recorded in `design.md` §6 is to keep 6px until that geometry can be regenerated
and reviewed live. Lowering the 15px window instead is rejected: a large surface
with a tight corner reads square, and the mismatch is in the container tier, not
the window.
