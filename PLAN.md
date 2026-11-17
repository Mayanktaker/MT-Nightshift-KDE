© Mayanktaker Computers & Web Development | https://mayanktaker.com

# MT Dark KDE — modernization plan

Working list. Closed items and their evidence (measurements, captures, commands) live in
[`plan-archive.md`](plan-archive.md); they are moved there when they close so this file stays
the current state rather than the history.

## Steps

- [ ] In a hands-on desktop pass, open the panel context menu and a tooltip (the panel Opaque state and the launcher/widget-explorer popups were checked on 2026-11-16; right-click and hover cannot be injected into this Wayland session — no `ydotool`/`kdotool` or `/dev/uinput`).
- [ ] Click the editable path field once by hand to confirm the 15px accent ring around a Base fill. The editable field itself was verified live on 2026-11-16 (15px taper, `#0A0B0D` fill, no frame pixels) after Dolphin's "Editable Location" action; AT-SPI's `SetFocus`/`Press` actions did not focus `KUrlNavigator` on Wayland, so the ring remains unconfirmed live and is still asserted offscreen by `check-style.py`.
- [ ] In a session without a custom `[General] AccentColor`, confirm the lighter Nord Night selected alternate row live. This session's accent override (`33,98,138`) governs Qt's selection fill, so the `Selection.BackgroundAlternate` step (`#93B3D1` over `#84A5C6`) is proven by the palette audit and offscreen probe, not by a live pill; see `validation.md`.

## Five named variants (2026-11-17)

Five named looks are installed and selectable: `nightshift` (default), `dayshift`, `nord-night`, `nord-day` and `one-dark-pro`. `make apply VARIANT=<name>` selects one and `make verify-live VARIANT=<name>` checks it; `apply-dayshift`, `apply-nord-night`, `apply-nord-day` and `apply-one-dark-pro` are aliases. All theme packages are 1.6.1, the Qt style plugin is unchanged at 1.4.0, and the decoration's frame line and five buttons are generated from each variant's palette. Qt Widgets menus (including submenus) and their hovered rows, plus hovered/pressed/checked tool buttons, now use the same 15px surface language as the field family; Plasma QML popups and the notification history are unchanged. The closed Nord, One Dark Pro and rounded-menu work, with its measurements and live capture paths, is in [`plan-archive.md`](plan-archive.md).

## Desktop Wallpapers (2026-11-17)

A complete 20-wallpaper abstract suite matching the exact palette blocks of all five looks is provided in `Wallpapers/` (Full HD 1920x1080, Dual-FHD 3840x1080 32:9, Dual-QHD 5120x1440 32:9, and 4K UHD 3840x2160). Managed by `tools/wallpapers/build-wallpapers.py` with lossless source masters under `Wallpapers/sources/`, rebuildable via `make wallpapers` and verified by `make check`. Detailed prompts, resolutions and provenance are documented in [`Wallpapers/README.md`](Wallpapers/README.md).

## Chosen direction

Nightshift OLED is the selected mockup: dark, calm, and high-contrast without turning every surface pure black. Keep Breeze's blue identity, but use it selectively for focus, selection, and active controls. Favor opaque, solid surfaces and deliberate edges over gradients, blur, and glow.


## Baseline and scope


The current baseline is the host's official Fedora KDE Plasma 6.8.2 assets: the complete shared `default/` Plasma Style asset folder, Breeze Dark's `breeze-dark/` metadata/palette, and the global `BreezeDark.colors` file. The Plasma Style inherits shared assets from `default/`; the copy is unmodified under `upstream/`.

This plan covers the Plasma desktop theme, global color scheme, Look-and-Feel manifest, Aurorae decoration and Qt Widgets style plugin. The style plugin is built against Qt 6.11.2 and wraps the installed Breeze style; it requires system plugin installation to appear in the selector and must be rebuilt after incompatible Qt updates. Cursors and other Breeze components are not replaced.
