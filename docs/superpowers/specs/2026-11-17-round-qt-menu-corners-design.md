© Mayanktaker Computers & Web Development | https://mayanktaker.com

# Round Qt menu corners — short design

## Intent

Dolphin's hamburger menu and its submenu (and Qt Widgets menus everywhere) still
show Breeze's small outer radius next to this theme's 15px control language. The
selected row is already a rounded pill; only the menu surface is square-ish.
Bring the outer menu surface to the same 15px corner language. Plasma QML popups
and the notification history are explicitly out of scope.

## Goals

- QMenu surfaces — including submenus — paint a 15px rounded `Window` fill with
  the theme's 1px `Frame` hairline, matching the field/control family.
- Menu item geometry, hover/selection pills, icons, shortcuts and separators stay
  where Breeze puts them; no layout shift.
- The offscreen probe asserts the corner taper, and a live Dolphin check confirms
  both the menu and its submenu.

## Non-goals / anti-goals

- No Plasma QML changes (notification popup radius is hardcoded in
  `NotificationPopup.qml`; Plasma menus use `solid/widgets/tooltip` at 6px).
- No stylesheet hacks, no app-specific code, no change to other QStyle surfaces.
- No new plugin, no geometry generator changes, no colour-scheme changes.

## Approaches

- **A. Intercept `PE_PanelMenu` / `PE_FrameMenu` in the QStyle proxy (chosen).**
  Qt's `QMenu` asks the style for both primitives, so one small C++ change covers
  every Qt Widgets menu and every submenu with no app coupling.
- **B. Qt stylesheet on QMenu.** App-specific and fragile; rejected.
- **C. Grow the Plasma tooltip asset.** Affects QML popups, not Dolphin's Qt
  menu; rejected.

## How it will work

- Add two cases to `MTNightshiftStyle::drawPrimitive` in
  `application-style/src/mtnightshiftstyle.cpp`: paint the menu panel with the
  existing `paintSurface()` helper at `kControlRadius` (15px), using the active
  palette's `Window` fill and the `Frame`-derived hairline; answer `PE_FrameMenu`
  with a matching rounded hairline (or suppress it if the panel already carries
  the edge), so Breeze's square frame cannot stamp the corners.
- Keep Breeze's `PM_MenuPanelWidth` margins and all item rendering: only the
  surface and its frame are owned. Verify that item backgrounds do not paint
  over the rounded corners; if Breeze's hover/selection extends to the rect
  edge, clip `CE_MenuItem` to the same rounded path in `drawControl()`.
- Add a corner-taper assertion to `tools/style-probe/check-style.py` against the
  existing `menu.png` render from `render-fields.cpp`. The probe currently
  renders no menu assertions, so this closes a real coverage gap.
- Live check: open Dolphin's hamburger menu and its submenu through AT-SPI on an
  accessibility-enabled Dolphin (this Wayland session has no pointer injection),
  capture with `spectacle -b -n -o`, measure the corner recession, and restore
  any session settings touched.

## Risks / review focus

- Breeze may draw the menu background as a cached pixmap with its own margins;
  the new fill must not leave a square halo behind.
- Item highlights that reach the menu edge would flatten the corners; clip if
  needed and re-check the screenshot.
- The style is global: verify at least one other Qt app's context menu.

## What's left to the builder

Exact helper call and hairline colour follow the existing code; the final
decision on clipping `CE_MenuItem` is made from the probe and live screenshot.
