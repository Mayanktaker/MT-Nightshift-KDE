© Mayanktaker Computers & Web Development | https://mayanktaker.com

# MT One Dark Pro Variant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one full One Dark Pro dark variant (scheme, Plasma Style, Look-and-Feel, Aurorae) with MIT provenance, registered across all existing tooling.

**Architecture:** The five variants are declared in four registries — `check-theme.py`, `build-decoration.py`, `check-buttons.py`, `Makefile` — with a fifth scheme render in `check-style.py`. Geometry stays generated and the Qt plugin stays shared and palette-driven. All packages report 1.6.0.

**Tech Stack:** KDE Plasma 6.8.2, Python 3 (generator/audit/probes), SVG/XML, Make, `kpackagetool6`, `kwriteconfig6`, Spectacle, Qt 6 offscreen probe.

**Spec:** `docs/superpowers/specs/2026-11-17-mt-one-dark-pro-variant-design.md`

**Execution note:** the current checkout is `main`; implementation must run in an isolated worktree, never on `main`.

## Global Constraints

- All packages report version **1.6.0**; plugin version unchanged; widget style key **MTNightshift** for all five.
- Text floor **4.66:1**, non-text **3:1**, focus stronger than hover.
- Scheme, style `colors`, LAF `contents/colors` are byte-identical, including the MIT credit header.
- One Dark Pro is MIT: `LICENSE.txt` says Copyright (c) 2013-2022 Binaryify; notice and license text must travel with the derived palette.
- Decoration and five button SVGs are generated, never hand-edited; padding 32 / border 6 in `.rc`.
- No changes to the four existing palettes, packages or artwork tones.
- This Wayland session has no pointer injection; capture with `spectacle -b -n -o <path>` and use the DBus recipe in `AGENTS.md`.

## Review Focus

- **MIT provenance travels with the palette:** all copies carry the notice — Task 1 asserts byte identity and the header text.
- **Upstream tones that fail the floor:** inactive text, negative, visited, focus ring and selection fill are lifted — Task 1's audit run proves the final values.
- **Generator palette vs scheme drift:** the new variant must join the cross-check — Task 2 confirms `check-buttons.py` rejects a divergent scheme copy.
- **Fifth render actually runs:** style probe and `make check` cover all five — Task 3 checks the render directory and `SCHEMES` entry.
- **Aurorae id wiring:** the new decoration name must match the LAF default — Task 3 dry-runs all five variants.

---

### Task 1: One Dark Pro scheme, packages and provenance

**Files:**
- Create: `color-schemes/MT-One-Dark-Pro.colors`, `LICENSES/MIT.txt`
- Create: `themes/mt-one-dark-pro/`, `themes/mt-one-dark-pro-global/`, `themes/aurorae/MTOneDarkPro/`
- Modify: `tools/theme-audit/check-theme.py`, `LICENSES/README.md`, `README.md`, `validation.md`
- Test: `python3 tools/theme-audit/check-theme.py`

**Interfaces:**
- Consumes: spec palette mapping, naming table and MIT notice.
- Produces: a fifth audit entry with `name: "One Dark Pro"`, `style_id: "mt-one-dark-pro"`, scheme/style/laf/aurorae paths; LAF id `com.mayanktaker.mt-one-dark-pro.desktop`.

- [ ] **Step 1: Add the One Dark Pro entry to `VARIANTS` in `check-theme.py`** using the spec's exact paths. Run the audit and confirm it fails on missing paths.
- [ ] **Step 2: Copy the upstream MIT text into `LICENSES/MIT.txt`** verbatim from One Dark Pro's `LICENSE.txt`, and add one pointer line each to `LICENSES/README.md` and `README.md` stating the derived palette's provenance and that KDE/LGPL boundaries are unchanged.
- [ ] **Step 3: Write `color-schemes/MT-One-Dark-Pro.colors`** from the spec's palette mapping: all `Colors:*` groups, `General.ColorScheme=MT-One-Dark-Pro`, `[WM]`, the KDE contributor notices, plus `SPDX-FileCopyrightText: 2013-2022 Binaryify` and a pointer to `LICENSES/MIT.txt`.
- [ ] **Step 4: Create the three package folders** from their Nightshift counterparts, substituting spec ids and version **1.6.0**; copy the scheme byte-for-byte into style `colors` and LAF `contents/colors`; set LAF defaults to the matching scheme/style/decoration `__aurorae__svg__MTOneDarkPro` and widget style `MTNightshift`. Aurorae `.rc` keeps padding 32 / border 6.
- [ ] **Step 5: Run the audit until all five variants pass**, adjusting only tones the audit rejects; record final measured floors and each upstream-to-final lift in `validation.md`.
- [ ] **Step 6: Commit**

```bash
git add color-schemes themes tools/theme-audit/check-theme.py LICENSES README.md validation.md
git commit -m "feat(theme): add One Dark Pro scheme and packages"
```

### Task 2: Generated artwork and scheme cross-check

**Files:**
- Modify: `tools/decoration-probe/build-decoration.py` (VARIANTS), `tools/decoration-probe/check-buttons.py` (SCHEMES)
- Regenerate: `themes/aurorae/MTOneDarkPro/{decoration,close,minimize,maximize,restore,menu}.svg`
- Test: `python3 tools/decoration-probe/check-buttons.py`

**Interfaces:**
- Consumes: Task 1's scheme and paths.
- Produces: a fifth `build-decoration.py` `VARIANTS` entry and a fifth `check-buttons.py` `SCHEMES` entry; generated artwork matching both.

- [ ] **Step 1: Add the fifth `VARIANTS` entry** with the scheme's header/window/foreground/negative/selection tones and an explicit `frame_line` token. Run `build-decoration.py --check`; confirm it fails on missing One Dark Pro artwork.
- [ ] **Step 2: Add the fifth `SCHEMES` entry to `check-buttons.py`** pointing at `color-schemes/MT-One-Dark-Pro.colors`. Demonstrate RED without modifying committed files: import the checker in a scratch Python process, point `SCHEMES["one-dark-pro"]` at a `/tmp` copy of the scheme with one role changed, call `check_scheme_palette("one-dark-pro", palette)`, and report the failing role and non-zero result. Restore nothing in the repo.
- [ ] **Step 3: Generate the five artwork files** with `build-decoration.py --variant one-dark-pro`, then run `build-decoration.py --check`, `check-buttons.py` and `check-decoration.py themes/aurorae/MTOneDarkPro/decoration.svg`; all must pass.
- [ ] **Step 4: Run `make check`** (all five variants, five renders); all checks must pass.
- [ ] **Step 5: Commit**

```bash
git add tools/decoration-probe themes/aurorae/MTOneDarkPro
git commit -m "feat(decoration): generate One Dark Pro artwork"
```

### Task 3: Fifth style render and named-variant Makefile

**Files:**
- Modify: `tools/style-probe/check-style.py`, `Makefile`

**Interfaces:**
- Consumes: Task 1's scheme; Task 2's decoration id.
- Produces: `one-dark-pro` in the `SCHEMES` table of `check-style.py` with its reference `window_rgb`, `pill_text_rgb`, `accent_rgb`; a fifth Makefile variant row and render.

- [ ] **Step 1: Add the fifth entry to `check-style.py`'s `SCHEMES`** using the audit-approved scheme values; the new reference tones must come from the scheme, not from Nightshift.
- [ ] **Step 2: Add `one-dark-pro` to `Makefile`'s `STYLE_SCHEMES` and variant table**, with style `mt-one-dark-pro`, scheme `MT-One-Dark-Pro`, decoration `__aurorae__svg__MTOneDarkPro` and LAF derived from the style id. Keep all five existing aliases working and default `VARIANT=nightshift`.
- [ ] **Step 3: Verify dry runs** — `make -n apply VARIANT=one-dark-pro` must name the four ids above and install the new packages; invalid `VARIANT` must still fail loudly.
- [ ] **Step 4: Run `make check` and `make check-dpr2`**; the fifth render must run and all checks must pass.
- [ ] **Step 5: Commit**

```bash
git add tools/style-probe/check-style.py Makefile
git commit -m "feat(build): register the One Dark Pro variant"
```

### Task 4: Live verification and final docs

**Files:**
- Modify: `AGENTS.md`, `design.md`, `validation.md`, `PLAN.md`, `plan-archive.md`
- Test artifacts: `/tmp/opencode/one-dark-pro-*.png`

**Interfaces:**
- Consumes: Tasks 1–3; the DBus/Spectacle recipe in `AGENTS.md`.

- [ ] **Step 1: Record the active scheme, style, decoration and `frameContrast`** with `kreadconfig6` so the session can be restored.
- [ ] **Step 2: Apply with `make apply VARIANT=one-dark-pro`**, run `make verify-live VARIANT=one-dark-pro`, and capture the desktop on a dark and a light wallpaper section with `spectacle -b -n -o`. Check the titlebar buttons and frame line are legible on both.
- [ ] **Step 3: Restore the recorded theme** and re-run `make verify-live` to prove the session is back where it started.
- [ ] **Step 4: Update the docs** — five-variant lists and pointers, final contrast measurements and MIT trail in `validation.md`, palette section in `design.md`, closed item evidence in `plan-archive.md`, open items in `PLAN.md`.
- [ ] **Step 5: Run `make check` and `make check-dpr2`, then commit**

```bash
git add AGENTS.md design.md validation.md PLAN.md plan-archive.md
git commit -m "docs(theme): record One Dark Pro variant and live verification"
```
