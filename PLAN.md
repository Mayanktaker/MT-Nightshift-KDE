© Mayanktaker Computers & Web Development | https://mayanktaker.com

# MT Dark KDE — modernization plan

Working list. Closed items and their evidence (measurements, captures, commands) live in
[`plan-archive.md`](plan-archive.md); they are moved there when they close so this file stays
the current state rather than the history.

## Steps

- [ ] Capture the maximized and inactive-window states live; the SVG probes already assert the maximized strip and the
  inactive fills, but no screenshot covers them.
- [ ] In a hands-on desktop pass, set the panel to Opaque and open a panel context menu and tooltip; session application and base panel appearance were checked, while these individual popup states were not manually opened.
- [ ] Confirm the editable path field by clicking it (no KIO development headers here, so a harness cannot instantiate a real KUrlNavigator): the expected result is our 15px accent ring around a Base fill.

## Chosen direction

Nightshift OLED is the selected mockup: dark, calm, and high-contrast without turning every surface pure black. Keep Breeze's blue identity, but use it selectively for focus, selection, and active controls. Favor opaque, solid surfaces and deliberate edges over gradients, blur, and glow.


## Baseline and scope


The current baseline is the host's official Fedora KDE Plasma 6.8.2 assets: the complete shared `default/` Plasma Style asset folder, Breeze Dark's `breeze-dark/` metadata/palette, and the global `BreezeDark.colors` file. The Plasma Style inherits shared assets from `default/`; the copy is unmodified under `upstream/`.

This plan covers the Plasma desktop theme, global color scheme, Look-and-Feel manifest, Aurorae decoration and Qt Widgets style plugin. The style plugin is built against Qt 6.11.2 and wraps the installed Breeze style; it requires system plugin installation to appear in the selector and must be rebuilt after incompatible Qt updates. Cursors and other Breeze components are not replaced.
