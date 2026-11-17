© Mayanktaker Computers & Web Development | https://mayanktaker.com

# Round Tab Bars Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Round Qt tab bars globally and determine whether the status strip is style-reachable.

**Architecture:** A new private paint helper owns `CE_TabBarTabShape`; Breeze keeps `CE_TabBarTabLabel`. Forced-state renders feed palette-agnostic taper assertions. A QStatusBar probe decides whether `PE_PanelStatusBar` is worth owning.

**Tech Stack:** C++17 / Qt 6 Widgets, CMake, Python probe, Spectacle + AT-SPI.

**Spec:** `docs/superpowers/specs/2026-11-17-round-tab-bars-design.md`

**Execution note:** isolated worktree; merge and rebuild in canonical checkout before install.

## Global Constraints

- Reuse `kControlRadius`, `kFrameContrast`, `stateFill()`; no new constants.
- Plugin version 1.4.0; schemes, packages, decoration and generators untouched.
- All five schemes must pass the probe.

## Review Focus

- Breeze stamping its tab background over ours — probe must measure pixels.
- Adjacent tabs clipping the rounded corners — clamp radius to tab height.
- Labels/icons lost — assert text pixels survive on the tab.
- Inactive tabs changing by accident — assert inactive render keeps its tone.
- Status strip app-painted — probe first, no speculative fix.

---

### Task 1: Rounded tab shapes and probe

**Files:** `application-style/src/mtnightshiftstyle.{h,cpp}`, `tools/style-probe/render-fields.cpp`, `tools/style-probe/check-style.py`

- [ ] **Step 1:** add forced `QTabBar` renders (active + inactive tabs) to `render-fields.cpp` via `CE_TabBarTabShape` and save `tab-active.png` / `tab-inactive.png`.
- [ ] **Step 2:** add taper assertions ≥8px for both renders to `check-style.py`; run `make check-style` and confirm RED.
- [ ] **Step 3:** add `paintTabShape(const QStyleOptionTab*, QPainter*) const`, handle `CE_TabBarTabShape` in `drawControl()`, delegate `CE_TabBarTabLabel`; clamp radius to tab height.
- [ ] **Step 4:** run `make check-style` until all five schemes pass, asserting text pixels survive; run `make check`.
- [ ] **Step 5:** commit `feat(style): round Qt tab bar shapes`.

### Task 2: Status-bar probe, live check, docs

**Files:** `application-style/src/mtnightshiftstyle.{h,cpp}` only if probe proves reach; `design.md`, `validation.md`, `PLAN.md`, `plan-archive.md`

- [ ] **Step 1:** add a `QStatusBar` render plus a temporary probe counter for `PE_PanelStatusBar`; record whether Dolphin-style status bars ask the style. If not reached, leave the strip alone and document it.
- [ ] **Step 2:** live Kate capture through `QT_PLUGIN_PATH` (`/tmp/opencode/tab-kate.png`) showing rounded tabs; if the session locks, use offscreen evidence and record the limit.
- [ ] **Step 3:** update docs with measurements, capture paths and the status-bar verdict; run `make check`.
- [ ] **Step 4:** commit `docs(theme): record rounded tab bars and status-bar probe`.
