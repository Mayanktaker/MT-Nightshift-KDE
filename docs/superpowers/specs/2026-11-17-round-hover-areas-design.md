© Mayanktaker Computers & Web Development | https://mayanktaker.com

# Round menu highlights and toolbar buttons — short design

## Intent

The outer QMenu surface is already 15px, but its hovered row and the toolbar
buttons in Dolphin still read flat. Bring those two interaction states into the
same Sculpted language. Status bars and QML popups are out of scope.

## Goals

- A hovered or keyboard-selected `CE_MenuItem` gets an inset 15px pill; icon,
  text, shortcut, check mark and submenu arrow remain intact.
- QToolButton hover, pressed and checked states get a rounded surface; label
  and menu indicator remain Breeze's.
- Offscreen probes assert both, with live Dolphin captures.

## Non-goals

- No status bar, Places sidebar delegate, Plasma QML, scheme, decoration or
  generator changes. Separators and idle menu rows keep their current look.
- No new constants: reuse `kControlRadius`, `kFrameContrast`, `kItemInsetX/Y`.

## Constraints

- Qt 6.11 QStyle: `CE_MenuItem` (QStyleOptionMenuItem), `PE_PanelButtonTool`
  (QStyleOptionToolButton). Breeze stays the base style.
- All five schemes share the plugin; assertions must be palette-agnostic.
- This Wayland host has no pointer injection: use AT-SPI + Spectacle.

## Approaches

- **A. Own the two QStyle controls (chosen).** Paint the pill/rounded surface,
  then ask Breeze to draw content with the state that triggers its background
  cleared, as already done for item views. Global, no app coupling.
- **B. Stylesheet per app.** Rejected: app-specific and fragile.
- **C. Event filters on Dolphin.** Rejected: app-specific and brittle.

## How

- `paintMenuPill(const QStyleOptionMenuItem*, QPainter*)` fills an inset rounded
  rect with the item-view hover tone; `drawControl(CE_MenuItem)` paints it, then
  calls Breeze with a copy of the option whose MouseOver/Selected flags are
  cleared so Breeze draws icon/text without its old highlight. Separators and
  non-hover rows delegate unchanged.
- `paintToolButton(const QStyleOptionToolButton*, QPainter*)` fills a rounded
  hover/pressed/checked surface; `drawPrimitive(PE_PanelButtonTool)` paints it.
  Labels and popup arrows stay with Breeze's `CC_ToolButton` paint path. Idle
  buttons keep Breeze's look.
- `render-fields.cpp` gains forced-state renders (menu with hovered row, tool
  buttons in normal/hover/pressed/checked); `check-style.py` asserts corner
  recession ≥ 8px on the state surfaces and that idle rows remain unchanged.

## Risks

- Breeze may still stamp its own highlight when flags are cleared; the probe
  must compare pixel evidence, not assume.
- Tool buttons with popup indicators may lose their arrow if the panel is
  owned; the probe renders `CC_ToolButton` with `HasMenu` to guard it.
