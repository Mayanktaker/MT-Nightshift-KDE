© Mayanktaker Computers & Web Development | https://mayanktaker.com

# Round Hover Areas Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give QMenu hover rows and QToolButton hover/pressed/checked states the theme's rounded pill language.

**Architecture:** Two new private paint helpers in the QStyle proxy own the background of `CE_MenuItem` and `PE_PanelButtonTool`; Breeze keeps drawing labels, icons and arrows from a state-stripped option. The offscreen probe gains forced-state renders and palette-agnostic taper assertions.

**Tech Stack:** C++17 / Qt 6 Widgets QProxyStyle, CMake, Python offscreen probe, Spectacle + AT-SPI.

**Spec:** `docs/superpowers/specs/2026-11-17-round-hover-areas-design.md`

**Execution note:** work in an isolated worktree, never on `main`.

## Global Constraints

- Reuse `kControlRadius = 15.0`, `kItemInsetX`, `kItemInsetY`, `kFrameContrast`; no new constants.
- Idle menu rows, separators and idle tool buttons keep Breeze's current look.
- Icons, text, shortcuts, check marks, submenu arrows and tool-button labels stay Breeze-rendered.
- Plugin version stays 1.4.0; schemes, packages, decoration and generators untouched.
- Wayland has no pointer injection: AT-SPI + `spectacle -b -n -o`.

## Review Focus

- Breeze stamping its old highlight over our pill — the probe must measure the hovered-row surface, not trust the paint order.
- Tool-button popup arrow disappearing — live hamburger capture must show the arrow.
- Idle states changing by accident — assert idle render unchanged against a baseline.
- State-stripped option losing text contrast — check text pixels remain readable on the pill.
- Five-scheme consistency — probe runs for all five schemes.

---

### Task 1: Rounded menu hover rows

**Files:** `application-style/src/mtnightshiftstyle.{h,cpp}`, `tools/style-probe/render-fields.cpp`, `tools/style-probe/check-style.py`

- [ ] **Step 1:** extend `render-fields.cpp` to render a QMenu with its first row forced to `State_MouseOver` into `menu-hover.png`, keeping the existing `menu.png`.
- [ ] **Step 2:** run `make check-style` after adding an assertion that `menu-hover.png` has a corner/inner taper of ≥8px through the existing `taper()` helper; confirm it FAILS on Breeze's current row.
- [ ] **Step 3:** add `paintMenuPill(const QStyleOptionMenuItem*, QPainter*) const` and handle `CE_MenuItem` in `drawControl()`: paint the inset pill for hover/selected rows, then delegate content drawing to Breeze with MouseOver/Selected cleared on a copy of the option. Separators and idle rows delegate unchanged.
- [ ] **Step 4:** run `make check-style` until the hover assertion passes and the idle `menu.png` assertions stay green. Record pixel evidence in the commit message.
- [ ] **Step 5:** run `make check`, commit: `feat(style): round menu hover rows`.

### Task 2: Rounded tool-button states and live verification

**Files:** `application-style/src/mtnightshiftstyle.{h,cpp}`, `tools/style-probe/render-fields.cpp`, `tools/style-probe/check-style.py`, `design.md`, `validation.md`, `PLAN.md`, `plan-archive.md`

- [ ] **Step 1:** add forced-state tool-button renders (hover, pressed, checked, idle) to `render-fields.cpp` and assertions of ≥8px corner recession on the state surfaces; run `make check-style` and confirm RED.
- [ ] **Step 2:** add `paintToolButton(const QStyleOptionToolButton*, QPainter*) const` and handle `PE_PanelButtonTool` in `drawControl()`: paint the rounded state surface, then delegate `PE_PanelButtonToolLabel`; idle buttons delegate unchanged.
- [ ] **Step 3:** run `make check-style` until all state assertions pass and idle remains unchanged.
- [ ] **Step 4:** live Dolphin check with the freshly built plugin via `QT_PLUGIN_PATH`: open the hamburger menu through AT-SPI, capture the hovered row (`/tmp/opencode/hover-menu.png`) and the toolbar buttons (`/tmp/opencode/hover-toolbar.png`); confirm the popup arrow is still drawn.
- [ ] **Step 5:** restore any session values touched, update docs with measurements and capture paths, run `make check`, and commit: `feat(style): round tool button states and record hover evidence`.
