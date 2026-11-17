© Mayanktaker Computers & Web Development | https://mayanktaker.com

# Round tab bars and probe the status bar — short design

## Intent

Kate's tab bar is the most visible remaining flat Qt surface. Round it globally
for Qt Widgets apps. Also determine whether Dolphin's status strip is reachable
from the style before deciding to restyle it.

## Goals

- Active and inactive `QTabBar` tabs paint rounded shapes; labels and icons stay
  with Breeze. Radius is clamped to tab height.
- `PE_PanelStatusBar` is probed; if apps ask the style, the strip can be rounded
  later. No speculative app-specific hack.
- Offscreen assertions cover tab states for all five schemes.

## Non-goals / anti-goals

- No Plasma QML panel or tray changes.
- No change to Dolphin status bar unless the probe proves the style is asked.
- No scheme, decoration, generator or version changes.

## Approaches

- **A. Own `CE_TabBarTabShape` in the QStyle proxy (chosen).** Global, no app
  coupling; delegate `CE_TabBarTabLabel` so text and icons keep Breeze rendering.
- **B. Per-app stylesheets.** Rejected: fragile and app-specific.
- **C. Fork Breeze.** Rejected: licensing and maintenance burden.

## Constraints

- Reuse `kControlRadius`, `kFrameContrast`, `stateFill()`; no new constants.
- Idle tabs keep their current look except for the corner shape; active tab fill
  follows the scheme's Highlight tone as other active surfaces do.
- Plugin stays 1.4.0; all five scheme packages untouched.

## How

- Add `paintTabShape(const QStyleOptionTab*, QPainter*) const`, handling
  `CE_TabBarTabShape` in `drawControl()`; delegate `CE_TabBarTabLabel`.
- Render forced active/inactive tabs into `tab-active.png` / `tab-inactive.png`
  and assert corner recession ≥ 8px in `check-style.py` for all five schemes.
- Status bar: render a `QStatusBar` through `render-fields.cpp` and add a probe
  that reports whether `PE_PanelStatusBar` is requested; if not, document that
  the flat strip is app-painted and out of reach.

## Risks

- Tab corners can be cropped by neighbouring tabs; clamp radius to tab height
  and verify the seam visually.
- Breeze may draw its own tab background over ours; the probe must measure the
  rendered pixels, not assume paint order.
