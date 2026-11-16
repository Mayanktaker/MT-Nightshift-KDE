© Mayanktaker Computers & Web Development | https://mayanktaker.com

# MT Dark KDE — modernization plan

Working list. Closed items and their evidence (measurements, captures, commands) live in
[`plan-archive.md`](plan-archive.md); they are moved there when they close so this file stays
the current state rather than the history.

## Steps

- [ ] In a hands-on desktop pass, open the panel context menu and a tooltip (the panel Opaque state and the launcher/widget-explorer popups were checked on 2026-11-16; right-click and hover cannot be injected into this Wayland session — no `ydotool`/`kdotool` or `/dev/uinput`).
- [ ] Click the editable path field once by hand to confirm the 15px accent ring around a Base fill. The editable field itself was verified live on 2026-11-16 (15px taper, `#0A0B0D` fill, no frame pixels) after Dolphin's "Editable Location" action; AT-SPI's `SetFocus`/`Press` actions did not focus `KUrlNavigator` on Wayland, so the ring remains unconfirmed live and is still asserted offscreen by `check-style.py`.

## Chosen direction

Nightshift OLED is the selected mockup: dark, calm, and high-contrast without turning every surface pure black. Keep Breeze's blue identity, but use it selectively for focus, selection, and active controls. Favor opaque, solid surfaces and deliberate edges over gradients, blur, and glow.


## Baseline and scope


The current baseline is the host's official Fedora KDE Plasma 6.8.2 assets: the complete shared `default/` Plasma Style asset folder, Breeze Dark's `breeze-dark/` metadata/palette, and the global `BreezeDark.colors` file. The Plasma Style inherits shared assets from `default/`; the copy is unmodified under `upstream/`.

This plan covers the Plasma desktop theme, global color scheme, Look-and-Feel manifest, Aurorae decoration and Qt Widgets style plugin. The style plugin is built against Qt 6.11.2 and wraps the installed Breeze style; it requires system plugin installation to appear in the selector and must be rebuilt after incompatible Qt updates. Cursors and other Breeze components are not replaced.
