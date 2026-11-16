© Mayanktaker Computers & Web Development | https://mayanktaker.com

# MT Nord KDE Variants Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add canonical Nord Night and Nord Day variants alongside Nightshift/Dayshift, and fix the shared decoration generator so all four variants have correct button and frame-line colours.

**Architecture:** Palette data lives in the two existing variant registries (decoration generator, theme audit); geometry stays shared and generated. The Qt style plugin is unchanged and palette-driven. The Makefile gains a named-variant table used by apply/install/verify-live, and the offscreen style probe gains per-scheme reference tones instead of Nightshift-hardcoded values.

**Tech Stack:** KDE Plasma 6.8.2, Python 3 (generator/audit/probe), CMake/Qt 6.11.2 (unchanged plugin), SVG/XML, Make, `kpackagetool6`, `kwriteconfig6`, Spectacle.

**Spec:** `docs/superpowers/specs/2026-11-16-mt-nord-kde-variants-design.md`

## Global Constraints

- All eight package metadata files report version **1.6.0**; `check-theme.py` requires one version across every registered variant. The plugin version is unchanged.
- Text contrast floor **4.66:1**, non-text **3:1** for every scheme, both directions; focus must measure stronger than hover.
- Style ids `mt-nightshift`, `mt-dayshift`, `mt-nord-night`, `mt-nord-day`; widget style key **MTNightshift** for all four.
- Aurorae padding **32** and border **6** must match the `.rc`; both decoration and button SVGs are generated, never hand-edited.
- `[KDE] frameContrast` is **0.05**, re-asserted after `plasma-apply-lookandfeel`.
- Palette copies in scheme, Plasma Style and Look-and-Feel are byte-identical.
- This Wayland session has no pointer injection; live changes use DBus shortcuts and `spectacle -b -n -o <path>` (recorded in `AGENTS.md`).

## Review Focus

- **Light-header titlebar icons:** Nord Day (and Dayshift) must not bake night-tone glyphs at ~1.5:1 against a light header — Task 2's button check asserts glyph and outline tone separation against each variant's header.
- **Pill text polarity:** Nord Night uses dark `#2E3440` text on a light selection pill, unlike the other three; Task 3's per-scheme probe asserts the correct text polarity instead of counting near-white pixels.
- **Frame line on light surfaces:** a derived light frame line can vanish on Nord Day's `#E5E9F0` header — Task 2 pins an explicit per-variant `frame_line` token and asserts it differs from the header fill.
- **Four-variant version drift:** adding packages at 1.0.0 breaks the single-version invariant — Task 1's audit run fails until every Nord package reports 1.6.0.
- **Palette copy drift:** new Plasma Style / LAF copies silently diverge from the scheme — Task 1's byte-identity audit covers all four variants.

---

### Task 1: Nord schemes and package skeleton

**Files:**
- Create: `color-schemes/MT-Nord-Night.colors`, `color-schemes/MT-Nord-Day.colors`
- Create: `themes/mt-nord-night/`, `themes/mt-nord-day/`, `themes/mt-nord-night-global/`, `themes/mt-nord-day-global/`, `themes/aurorae/MTNordNight/`, `themes/aurorae/MTNordDay/`
- Modify: `tools/theme-audit/check-theme.py` (VARIANTS list)
- Test: `python3 tools/theme-audit/check-theme.py`

**Interfaces:**
- Consumes: spec palette mapping and naming table; existing package layout as template.
- Produces: four audit-ready variant entries with `name`, `style_id`, `scheme`, `style`, `laf`, `aurorae` paths; package ids `com.mayanktaker.mt-nord-night.desktop` / `com.mayanktaker.mt-nord-day.desktop`.

- [ ] **Step 1: Add the two Nord entries to `VARIANTS` in `tools/theme-audit/check-theme.py`** using the spec's exact names and paths. Do not create the packages yet.
- [ ] **Step 2: Run `python3 tools/theme-audit/check-theme.py`; confirm it fails with missing Nord paths** — that is the failing test for this task.
- [ ] **Step 3: Write the two scheme files** by copying `MT-Nightshift.colors` / `MT-Dayshift.colors` and substituting the spec's palette mapping (all `Colors:*` groups, `General.Name`, `[WM]`, credits header unchanged). Use the spec's first-pass tones verbatim; tuning happens in Step 5.
- [ ] **Step 4: Create the six package folders** from their Nightshift/Dayshift counterparts, substituting ids, names and version **1.6.0** per the spec naming table; copy each scheme byte-for-byte into its style `colors` and LAF `contents/colors`; set LAF defaults to the matching scheme/style/decoration and widget style `MTNightshift`. Aurorae `metadata.desktop` and `.rc` keep the shared geometry values.
- [ ] **Step 5: Run `python3 tools/theme-audit/check-theme.py` until all four variants pass**, adjusting only Nord tones the audit rejects; record the final measured floors in `validation.md`.
- [ ] **Step 6: Commit**

```bash
git add color-schemes themes tools/theme-audit/check-theme.py validation.md
git commit -m "feat(theme): add Nord Night and Nord Day packages"
```

### Task 2: Generated frame lines and buttons for four variants

**Files:**
- Modify: `tools/decoration-probe/build-decoration.py` (VARIANTS, frame derivation, button generation, `--check`)
- Create: `tools/decoration-probe/check-buttons.py`
- Regenerate: `themes/aurorae/MT{Nightshift,Dayshift,NordNight,NordDay}/{decoration,close,minimize,maximize,restore,menu}.svg`
- Modify: `design.md` §12.2 (frame-line description)

**Interfaces:**
- Consumes: Task 1's four variant palettes and paths.
- Produces: `build-decoration.py --check` verifying all four decorations and all four button sets; each variant palette gains `foreground_inactive`, `negative`, `selection`, `selection_text`, `frame_line` alongside the existing four keys.

- [ ] **Step 1: Add Nord entries to `build-decoration.py`'s `VARIANTS`** with the spec's header/window/foreground tones and an explicit `frame_line` per variant. Run `python3 tools/decoration-probe/build-decoration.py --check`; confirm it fails on the missing Nord `decoration.svg` files.
- [ ] **Step 2: Replace the import-time `PARAMS["frame"] = blend(...)` with a per-variant assignment** so the drift loop applies each palette's `frame_line` before building; keep `frame_line_contrast` and the documented rationale in `PARAMS` for the derived interior seams.
- [ ] **Step 3: Implement `build_buttons(palette) -> dict[str, str]`** returning the five button SVGs (`close`, `minimize`, `maximize`, `restore`, `menu`) from the existing geometry templates: active glyph = `foreground`, inactive glyph = `foreground_inactive`, hover glyph/outline = `negative`, pressed fill = `selection`, pressed glyph = `selection_text`, hover-inactive outline = `foreground_inactive` (the `frame_line` whisper cannot clear the 3:1 state-cue floor against the inactive header). Keep every path, rect and `stroke-width` from the current artwork byte-for-byte; only colour values vary.
- [ ] **Step 4: Wire `--check` to compare all four decoration SVGs and all four button sets**, and write `check-buttons.py` asserting each generated set parses as XML, its state tones match the variant palette, and its hover-inactive ring clears **3:1** against `header_inactive` (fails on the current Dayshift button files).
- [ ] **Step 5: Regenerate all four variants' decoration and button SVGs**, run `xmllint --noout` on every SVG, then `build-decoration.py --check`, `check-buttons.py`, and `check-decoration.py` for each of the four decorations. Confirm Dayshift's regenerated buttons now read against its light header.
- [ ] **Step 6: Commit**

```bash
git add tools/decoration-probe themes/aurorae design.md
git commit -m "fix(decoration): generate variant frame lines and button tones"
```

### Task 3: Four-scheme offscreen style probe

**Files:**
- Modify: `tools/style-probe/check-style.py`, `Makefile` (`check-style` target)

**Interfaces:**
- Consumes: Task 1's four scheme files.
- Produces: `check-style.py <render-dir> [--ci] --scheme <name>` with a `SCHEMES` table giving reference `window_rgb`, `pill_text_rgb` and accent polarity for the four names; `--light` removed.

- [ ] **Step 1: Add the `SCHEMES` table and require `--scheme`, replacing `--light`** in `check-style.py`. Update the `Makefile` to render all four schemes into `build/style-probe/out-<name>` and invoke the checker with the matching `--scheme`.
- [ ] **Step 2: Run `make check-style`; confirm it fails** because the new Nord invocations have no reference data / the checker rejects the missing argument.
- [ ] **Step 3: Parameterise the hardcoded assertions** — the `[16,18,22]` window tone in `pill_shape`/`item frame dimmed`, and the near-white `item text on pill` count — to read `window_rgb` and `pill_text_rgb` from `SCHEMES`. Use the spec's first-pass values: Nightshift `[16,18,22]`/white, Dayshift `[243,245,248]`/white, Nord Night `[46,52,64]`/`[46,52,64]`, Nord Day `[236,239,244]`/white.
- [ ] **Step 4: Run `make check-style` until all four renders pass**, changing only the reference table where a genuine palette difference requires it; keep the invariants themselves unchanged.
- [ ] **Step 5: Commit**

```bash
git add tools/style-probe/check-style.py Makefile
git commit -m "test(style): probe all four schemes with per-variant reference tones"
```

### Task 4: Named-variant apply and verify-live

**Files:**
- Modify: `Makefile`

**Interfaces:**
- Consumes: Task 1's package ids/paths, Task 3's four-render check.
- Produces: `VARIANT=nightshift|dayshift|nord-night|nord-day` driving `LIVE_STYLE`, `LIVE_SCHEME`, `LIVE_DECORATION`, LAF id and install dirs; `make apply-nord-night` and `make apply-nord-day` aliases; existing `apply` / `apply-dayshift` unchanged in effect.

- [ ] **Step 1: Replace the `DAYSHIFT` conditionals with a variant lookup table** keyed by the four names, defaulting `VARIANT=nightshift`; keep the old target names as thin wrappers that set `VARIANT`.
- [ ] **Step 2: Extend `apply-install` to install all four Aurorae themes, all four schemes, all four Plasma Styles and all four Look-and-Feel packages.**
- [ ] **Step 3: Check the mapping with dry runs** — `make -n apply VARIANT=nord-night` must name `com.mayanktaker.mt-nord-night.desktop`, `MT-Nord-Night`, `mt-nord-night` and `__aurorae__svg__MTNordNight`; the same for `nord-day`. Confirm `make -n apply-dayshift` still names the Dayshift values.
- [ ] **Step 4: Run `make check` end to end** with the four-variant table in place; all checks must pass.
- [ ] **Step 5: Commit**

```bash
git add Makefile
git commit -m "feat(build): add named theme variants to apply and verify-live"
```

### Task 5: Live verification and documentation

**Files:**
- Modify: `README.md`, `design.md`, `validation.md`, `AGENTS.md`, `PLAN.md`, `plan-archive.md`
- Test artifacts: screenshots under `/tmp/opencode`

**Interfaces:**
- Consumes: Tasks 1–4; the DBus/Spectacle live-testing recipe in `AGENTS.md`.

- [ ] **Step 1: Record the currently active theme values** (`kreadconfig6` reads for scheme, Plasma Style, decoration, frameContrast) so they can be restored.
- [ ] **Step 2: Apply Nord Night** with `make apply VARIANT=nord-night`, run `make verify-live VARIANT=nord-night`, and capture the desktop plus a maximized window with `spectacle -b -n -o /tmp/opencode/nord-night.png`.
- [ ] **Step 3: Apply Nord Day** with `make apply VARIANT=nord-day`, run `make verify-live VARIANT=nord-day`, and capture `/tmp/opencode/nord-day.png`. Inspect both on the existing light wallpaper section; the titlebar icons and frame line must be legible.
- [ ] **Step 4: Restore the previously active theme** and re-run `make verify-live` to confirm the session is back where it started.
- [ ] **Step 5: Update the docs** — package list in `README.md`, palette/frame sections in `design.md`, final measured floors and live evidence in `validation.md`, the variant recipe pointer in `AGENTS.md`, and move the closed Nord items from `PLAN.md` to `plan-archive.md` with the measurements and capture paths.
- [ ] **Step 6: Run `make check` and `make check-dpr2`, then commit**

```bash
git add README.md design.md validation.md AGENTS.md PLAN.md plan-archive.md
git commit -m "docs(theme): record Nord variants and live verification"
```
