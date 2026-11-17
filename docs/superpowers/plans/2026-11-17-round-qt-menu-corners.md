© Mayanktaker Computers & Web Development | https://mayanktaker.com

# Round Qt Menu Corners Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give Qt Widgets menus — including Dolphin's hamburger menu and its submenu — the theme's 15px rounded surface and 1px hairline.

**Architecture:** The proxy style already owns rounded controls via `paintSurface`/`fillSurface`; it now also owns the QMenu surface through `PE_PanelMenu` and `PE_FrameMenu`. Item rendering and metrics stay delegated to Breeze. The offscreen probe gains a menu corner assertion, and a live Dolphin capture verifies the real popup.

**Tech Stack:** C++17 / Qt 6 Widgets QProxyStyle, CMake, Python offscreen probe (PIL/numpy), Spectacle + AT-SPI for live capture.

**Spec:** `docs/superpowers/specs/2026-11-17-round-qt-menu-corners-design.md`

**Execution note:** current checkout is `main`; implementation must run in an isolated worktree.

## Global Constraints

- Radius is **`kControlRadius = 15.0`**; outline width **`kOutlineWidth = 1.0`**; no new radius constant.
- Panel fill uses `QPalette::Window`; outline is the existing `kFrameContrast`-derived hairline from `Window`/`WindowText`.
- Breeze's `PM_MenuPanelWidth` margins and all `CE_MenuItem` rendering stay unchanged unless a corner overflow is proven.
- No Plasma QML, stylesheet, scheme, decoration or generator changes.
- Qt plugin version stays **1.4.0**; widget style key `MTNightshift`; all five themes unchanged.
- Wayland session has no pointer injection: use AT-SPI on an accessibility-enabled Dolphin and `spectacle -b -n -o <path>`.

## Review Focus

- **Square halo / cached Breeze pixmap:** the new fill must fully replace Breeze's menu background — Task 1's offscreen corner probe and a live capture assert the outer corners are rounded, not just overlaid.
- **Item backgrounds flattening corners:** a hover/selection rect reaching the menu edge must be clipped to the rounded path — Task 1 includes a live check of the selected "Actions for Current View" row near the corner and a `CE_MenuItem` clip only if needed.
- **Layout shift:** Breeze's `PM_MenuPanelWidth` margins must stay — Task 1's probe compares menu dimensions before and after and asserts they are unchanged.
- **Submenu coverage:** submenus are also QMenu — Task 2 captures the hamburger submenu live, not only the top-level menu.
- **Global side effects:** another Qt app's context menu must still render correctly — Task 2 includes one non-Dolphin check.

---

### Task 1: Rounded menu surface and offscreen assertion

**Files:**
- Modify: `application-style/src/mtnightshiftstyle.h`, `application-style/src/mtnightshiftstyle.cpp`
- Modify: `tools/style-probe/check-style.py`
- Test: `tools/style-probe/check-style.py` via `make check-style`

**Interfaces:**
- Consumes: existing `paintSurface(QPainter*, const QRectF&, qreal, qreal, const QColor&, const QColor&)` and `fillSurface(...)`; existing `menu.png` render from `render-fields.cpp`.
- Produces: `PE_PanelMenu` and `PE_FrameMenu` handled in `drawPrimitive`; a `menu outer corner taper` assertion in `check-style.py`.

- [ ] **Step 1: Add the failing assertion to `check-style.py`** for `menu.png`: using the existing `taper()` helper, require a corner recession of at least 8px on a menu render whose height is ~100px, and state the exact threshold in the assertion message. Run `make check-style` and confirm it fails on the current Breeze-rounded menu.
- [ ] **Step 2: Declare two private helpers in `mtnightshiftstyle.h`** — `bool paintMenuPanel(const QStyleOption *option, QPainter *painter) const` and `bool paintMenuFrame(const QStyleOption *option, QPainter *painter) const` — and implement them in the `.cpp` using `paintSurface()` at `kControlRadius` with the palette's `Window` fill and the existing `kFrameContrast` hairline. `paintMenuFrame` must not draw a square Breeze frame in its place.
- [ ] **Step 3: Add `PE_PanelMenu` and `PE_FrameMenu` cases** to `drawPrimitive()` that call those helpers and return when they succeed; all other primitives continue to delegate.
- [ ] **Step 4: Run `make check-style` until the new assertion passes**, adjusting only the menu paint path. Confirm the existing field-family assertions still pass and the menu render size is unchanged from the pre-change `menu.png` (69x100 at this Qt build).
- [ ] **Step 5: If the probe shows an item background covering a corner**, clip `CE_MenuItem` in `drawControl()` to the same rounded path for QMenu widgets only; otherwise leave item rendering delegated. Record the decision and the pixel evidence in the report.
- [ ] **Step 6: Run `make check` and commit**

```bash
git add application-style tools/style-probe/check-style.py
git commit -m "feat(style): round Qt menu surfaces to 15px"
```

### Task 2: Live verification and documentation

**Files:**
- Modify: `design.md`, `validation.md`, `PLAN.md`, `plan-archive.md`
- Test artifacts: `/tmp/opencode/qt-menu-*.png`

**Interfaces:**
- Consumes: Task 1's built plugin and assertion.

- [ ] **Step 1: Record the active theme values** with `kreadconfig6` (scheme, Plasma Style, decoration, frameContrast) before any live test.
- [ ] **Step 2: Launch Dolphin with `QT_ACCESSIBILITY=1` and the freshly built plugin** (`make style-preview APP=dolphin`), find the `Open Menu` button through AT-SPI, invoke it, and capture the menu with `spectacle -b -n -o /tmp/opencode/qt-menu-dolphin.png`. Then open its `Actions for Current View` submenu via AT-SPI and capture `/tmp/opencode/qt-menu-submenu.png`.
- [ ] **Step 3: Measure the outer corner recession** on both captures with PIL (target: 15px corner language, no square halo, no item highlight covering the corner). If it fails, go back to Task 1's paint/clip path before continuing.
- [ ] **Step 4: Check one other Qt app's context menu** (e.g. Kate or Konsole) with the same built plugin and capture it.
- [ ] **Step 5: Restore the session settings** recorded in Step 1. No theme apply is needed — the plugin is loaded per process — but confirm the live theme is still Nightshift with `make verify-live`.
- [ ] **Step 6: Update the docs** — shape section in `design.md`, menu corner evidence and probe limits in `validation.md`, closed item with measurements and capture paths in `plan-archive.md`.
- [ ] **Step 7: Run `make check`, then commit**

```bash
git add design.md validation.md PLAN.md plan-archive.md
git commit -m "docs(theme): record rounded Qt menu corners"
```
