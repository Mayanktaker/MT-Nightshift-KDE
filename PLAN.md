© Mayanktaker Computers & Web Development | https://mayanktaker.com

# MT Dark KDE — modernization plan

## Steps

- [x] Copy the official Breeze Dark color scheme and Plasma Style base into `upstream/` without modifying the source files.
- [x] Audit the palette, metadata, and inherited SVG assets; map surface, text, focus, selection, and semantic states before editing.
- [x] Create a separately named MT Dark Plasma Style and global color scheme, retaining the official baseline for comparison and safe rollback.
- [x] Apply the **Nightshift OLED** direction: near-black rather than pure black, restrained Breeze-blue focus, solid carbon surface layers, sharper separation, and polished control states; avoid blur/glass styling.
- [x] Install the theme and color scheme in user-local KDE directories and apply them in the Plasma 6.8.2 session; restore the prior selections afterward without replacing system files.
- [x] Document the install process, upstream credits, and licensing boundary.
- [x] Add a Plasma 6 Look-and-Feel package that selects the existing Plasma Style and color scheme without resetting user layout or personal settings.
- [x] Add a user-local Aurorae decoration with Sculpted 21px window corners; correct the FrameSvg corner names and add menu-button artwork after live review.
- [x] Implement and build a Qt Widgets style plugin over Breeze with Sculpted ~15px control surfaces; smoke-test it in an isolated Qt application.
- [x] Install the Global Theme and Aurorae decoration in user-local KDE paths and verify both are discoverable without changing active settings.
- [x] Install the compiled Qt style plugin and `.themerc` in Qt/KStyle system paths; verify plugin discovery, activate it and confirm a fresh Qt process uses `MTNightshift`.
- [x] Implement 12px Qt scrollbar gutters and a Dolphin Places-sidebar-only hidden gutter; verify the style metrics and preserve dialog scrollbars in an offscreen Qt test.
- [x] Update the installed Application Style plugin; verify a fresh Dolphin sidebar screenshot and offscreen metrics for hidden Places gutter (0px), other apps (12px), and Dolphin dialogs (12px).
- [x] Offscreen-test a long Places-view list: its scrollbar has 0px width while mouse-wheel events still advance the scroll position.
- [x] Remove the Dolphin Places dock divider and round/borderlessly fill framed line edits and non-editable combos; leave the integrated toolbar hairline intact rather than replace Breeze's full background paint.
- [ ] In live Dolphin, verify keyboard/touch scrolling with overflowing Places; visually inspect a 12px scrollbar in another Qt Widgets app.
- [ ] Restart Plasma and verify the Aurorae menu glyph, rounded corners, active/inactive states and maximized state.
- [ ] In a hands-on desktop pass, set the panel to Opaque and open a panel context menu and tooltip; session application and base panel appearance were checked, while these individual popup states were not manually opened.
- [x] Apply the Global Theme and Aurorae decoration; verify active IDs and preserve the user's Tela-circle icons and other omitted defaults.

## Chosen direction

Nightshift OLED is the selected mockup: dark, calm, and high-contrast without turning every surface pure black. Keep Breeze's blue identity, but use it selectively for focus, selection, and active controls. Favor opaque, solid surfaces and deliberate edges over gradients, blur, and glow.

## Baseline and scope

The current baseline is the host's official Fedora KDE Plasma 6.8.2 assets: the complete shared `default/` Plasma Style asset folder, Breeze Dark's `breeze-dark/` metadata/palette, and the global `BreezeDark.colors` file. The Plasma Style inherits shared assets from `default/`; the copy is unmodified under `upstream/`.

This plan covers the Plasma desktop theme, global color scheme, Look-and-Feel manifest, Aurorae decoration and Qt Widgets style plugin. The style plugin is built against Qt 6.11.2 and wraps the installed Breeze style; it requires system plugin installation to appear in the selector and must be rebuilt after incompatible Qt updates. Cursors and other Breeze components are not replaced.

## Verification

Validation completed: Global Theme metadata and bundled palette pass package checks; the Plasma Style and Aurorae decoration are discovered; all Plasma SVGZ and Aurorae SVG assets pass XML checks; shared palette groups match and the bundled scheme is byte-identical to the global scheme; the 128-pair WCAG 2.1 audit has zero failures (4.66:1 minimum). The Qt plugin builds, is installed in Qt's system plugin path, appears in `QStyleFactory`, and a new Qt process reports `objectName=mtnightshift`; a rendered control harness uses the dark palette (`Base=#0a0b0d`). The updated scrollbar plugin is installed; a fresh Dolphin screenshot shows no sidebar scrollbar, and offscreen metric tests report 0px for the Dolphin Places view, 12px for other views, and 12px in a Dolphin dialog. An overflowing test list retains a scroll range and responds to wheel events. Live keyboard/touch verification in Dolphin remains. The Global Theme, Aurorae decoration and Qt Application Style are active.

The path resolver confirms direct `solid/` and `translucent/` assets resolve inside MT Nightshift. The KDE color scheme had left partial `[Colors:*]` groups in `kdeglobals`, which shadowed the selected scheme and caused Qt's palette to default to white; switching away and reapplying MT Nightshift rewrote complete groups, now verified as `View=10,11,13` and `Window=16,18,22`. Remaining checks: restart KWin to refresh its cached Aurorae `menu.svg` path, then verify window states and existing panel/menu/tooltip checks.
