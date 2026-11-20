© Mayanktaker Computers & Web Development | https://mayanktaker.com

# Validation

How every claim in `design.md` is measured, and what the suite cannot see. One
concern: verification. Visual decisions live in `design.md`; scope and task
state live in `PLAN.md`.

## One entry point

```bash
make check          # artwork, palettes, packages, colour maths, style probe (five schemes)
make check-dpr2     # the same artwork rendered at 2x, where the corner arc is 1px
make package        # the release archives plus their isolated installer run
make verify-live    # the running session: config values, deployed copies, system plugin
make uninstall      # removes the user-local packages; `style-uninstall` the system plugin
```

`make check` and `make check-dpr2` run in CI (`.github/workflows/checks.yml`) on
every push and pull request, in two jobs: Ubuntu for speed and Fedora 45 for the
target platform, including the `kpackagetool6` package check that Ubuntu cannot
provide. `tools/git-hooks/pre-commit` runs the palette audit on every commit and
the decoration checks whenever Aurorae artwork is staged. `make verify-live`
needs a session, so it runs after `make apply` instead.

Three checks are easy to miss because they do not render anything:

- `make check-kpackages` installs all five Look-and-Feel packages into a
  throwaway `XDG_DATA_HOME` with `kpackagetool6`. It prints an explicit skip when
  the tool is absent rather than reporting a pass.
- `make check-math` compiles the shared colour helpers against edge inputs:
  endpoint blends, out-of-range weights (an unclamped `QColor::fromRgbF` returns
  an invalid colour that paints nothing), equal-tone contrast, unreachable
  contrast targets and the disabled/active palette-group precedence.
- `make package` executes every generated `install.sh` in a temporary `HOME` with
  a stub `kpackagetool6`, then asserts the colour scheme, desktop theme and
  decoration landed. The installer is also syntax-checked before that run.

`make uninstall` removes only the five named packages and schemes; a sentinel
theme and an unrelated `.colors` file survive it. `style-uninstall` refuses to
run when `qtpaths6` reports no plugin directory, so an empty variable cannot turn
into an `rm` against `/styles`.

The probe's `--ci` flag is passed only when `GITHUB_ACTIONS` is set, because the
Ubuntu image has no Breeze style. It skips frame suppression, the 12px scroll-bar
extent and the menu size/corner scan — all of which read the base style's own
metrics. A shell that merely exports `CI=true` still runs the full assertions,
which is the safe default. The Fedora job installs `plasma-breeze-qt6` and clears
`GITHUB_ACTIONS` for its check, so those assertions still run on every push.

## Palette and package audit — `tools/theme-audit/check-theme.py`

Standard-library only, so it costs nothing to run everywhere.

| Invariant | Rule |
| --- | --- |
| Palette copies | `color-schemes/<variant>.colors`, `themes/<style>/colors` and `themes/<style>-global/contents/colors` are byte-identical |
| Text contrast | every `Foreground*` role ≥ **4.66:1** against both `BackgroundNormal` and `BackgroundAlternate` of its own group — 8 groups × 8 roles × 2 backgrounds = 128 measurements per variant |
| Non-text contrast | `DecorationFocus` and `DecorationHover` ≥ **3:1** against `Window` and `Button`; selection fill ≥ 3:1 against `Window` |
| Accent hierarchy | focus contrast > hover contrast, whichever direction the palette needs |
| Package linkage | style `Id` = directory name; Look-and-Feel selects that scheme name, Plasma Style, decoration and `MTNightshift` widget style; Aurorae `X-KDE-PluginInfo-Name` matches its directory; every package reports one version |
| Decoration geometry | `Padding*`/`Border*` in both `.rc` files equal `PARAMS` in `build-decoration.py` |

**The 4.66 floor** is WCAG 2.1 AA (4.5:1) plus a 0.16 margin so a colour that
lands on the boundary after rounding still passes. Ratios use the relative
luminance formula on sRGB values with no rounding inside the calculation. Body
text runs far above it; the binding roles are the dim label (`ForegroundInactive`)
and the palette's semantic colours on the darkest or lightest alternate.

The script exits non-zero and names the failing pair, so a regression looks like
`4.07 (Button/Negative)` rather than a colour argument in review. It has been
proven to reject both defect classes that shipped before it existed: a drifted
copy and a dimmed negative.

### Measured floors

The audit's summary line names the lowest text ratio and its pair; the rings and
the selection fill are reported per surface. Current measurements, all above the
floors:

| Variant | Text floor | Window focus / hover | Button focus / hover | Selection vs Window |
| --- | --- | --- | --- | --- |
| Nightshift | 4.66 (Selection/Positive) | 5.67 / 4.20 | 5.00 / 3.70 | 3.36 |
| Dayshift | 4.66 (Selection/Positive) | 3.95 / 3.28 | 4.13 / 3.42 | 4.93 |
| Nord Night | 4.79 (Selection/Negative) | 6.24 / 4.86 | 5.03 / 3.92 | 4.86 |
| Nord Day | 4.69 (Selection/Visited) | 4.77 / 3.50 | 4.52 / 3.31 | 4.77 |
| One Dark Pro | 4.67 (Button/Neutral) | 5.92 / 4.57 | 3.95 / 3.05 | 4.33 |

The Nord schemes keep the design's canonical tones wherever they clear the
floors. `Selection.BackgroundAlternate` was adjusted in both variants, because
plain nord10 `#5E81AC` left dark pill text at 3.10:1 on Night and white pill
text at 4.03:1 on Day; the alternates are now `#93B3D1` (Night, lighter than the
pill) and `#405A79` (Day, deeper). Semantic tones were also tuned where the
canonical value missed: Night lifted negative, positive, active, link and
visited; Day deepened negative, active, link and visited. Every other tone is
the design's first pass verbatim.

**One Dark Pro lifts.** The spec's computed first-pass palette mapping
(`docs/superpowers/specs/2026-11-17-mt-one-dark-pro-variant-design.md`) keeps
every background verbatim, including the relatively light `#404754` button
face. On that surface the muted foregrounds fall below the 4.66 floor, so the
audit rejects them by name and each was lifted the minimum that clears it
while keeping its hue: inactive `#9DA5B4` → `#B2B8C4`, active/link `#61AFEF` →
`#7FBEF2`, visited `#CF7CE7` → `#E0A8F2`, negative `#F07B86` → `#F4A1A9`,
neutral `#D19A66` → `#DBAF86`, positive `#8CC265` → `#93C66E`, and the hover
ring `#528BFF` → `#5990FF` (the 3:1 non-text floor). The focus ring keeps the
signature `#61AFEF` verbatim — it only needs 3:1 and measures 3.95 on the button
face — which also keeps it stronger than the lifted hover on both audited
surfaces (5.92 / 4.57 on Window, 3.95 / 3.05 on Button). Body text `#D7DAE0`,
the `#528BFF` / `#61AFEF` selection fills, the `#1D1F23` selection ink and all
eight group backgrounds are the design's first pass unchanged. The binding
floor is now 4.67 (Button/Neutral); the spec's 5.92 / 4.33 focus-over-hover
claim becomes 5.92 / 4.57 after the ring lift. The seven lifts are the only
tones that differ from the spec's computed first pass; every other role matches
the §15 role descriptions in `design.md`.

**One Dark Pro provenance.** The palette is derived from Binaryify's One Dark
Pro (`oneDarkPro.ts`, the standard variant — not Flat or Mix), MIT licensed,
Copyright (c) 2013-2022 Binaryify. `LICENSES/MIT.txt` is the verbatim upstream
`LICENSE.txt` (verified by `diff -u` against
`https://raw.githubusercontent.com/Binaryify/OneDark-Pro/master/LICENSE.txt`);
`LICENSES/README.md` and `README.md` carry the pointer. The three shipped copies
of the scheme — `color-schemes/MT-One-Dark-Pro.colors`,
`themes/mt-one-dark-pro/colors` and
`themes/mt-one-dark-pro-global/contents/colors` — carry one
`SPDX-FileCopyrightText: 2013-2022 Binaryify` line each and keep the existing KDE
contributor notices. The audit verifies the three are byte-for-byte identical;
the KDE/LGPL boundary for the Breeze-derived assets is unchanged and no
endorsement is implied.

**Inactive-header derivation.** Breeze paints a selected/active row from the
focus token at 80% over its background (§2 of `design.md`), so a scheme's focus
tone must clear the floors *after compositing*, not just at rest. Nord's plain
focus `#88C0D0` measured 4.64:1 on the dark `Window` — just under the 4.66
floor — which is why Night's focus becomes `#84A5C6`. The inactive header is a
separate palette group, not a dimmed copy of the active one: Night pairs
`Header[Inactive]` `#2E3440` / alternate `#3B4252` against inactive text
`#D8DEE9` (the active header is `#3B4252` / `#2E3440` with `#ECEFF4`), and Day
pairs `#D8DEE9` / `#E5E9F0` against `#4C566A` (active `#E5E9F0` / `#D8DEE9`
with `#2E3440`). The audit measures every `Foreground*` role against *both*
backgrounds of its own group, so that inverted alternate and its dimmer title
tone are audited independently; the 4.79 (Night) and 4.69 (Day) floors are the
result, not an assumption.

**Selection-pill derivation.** A selected row is an 80% focus fill over the row
background, with text from the `Selection` group. Night's normal pill is
`#84A5C6` with dark `#2E3440` ink; its alternate row uses
`BackgroundAlternate`, which the canonical `#5E81AC` left at 3.10:1. Lifting
the alternate to `#93B3D1` (147,179,209) makes it **lighter** than the normal
`#84A5C6` (132,165,198) — a deliberate +15/+14/+11 channel step, so one dark
ink set works on both row states. Day inverted the fix: white pill text on
nord10 was 4.03:1, so its alternate was deepened to `#405A79`, which stays
darker than the normal `#4C6B91` pill. The offscreen style probe renders a
forced selected pill under each of the five schemes and asserts readable text
inside the pill's own bounding box (115/210/180/210 text pixels for
Nightshift/Dayshift/Nord Night/Nord Day), so the lighter Night alternate cannot
regress to a sub-floor fill unnoticed.

## Decoration artwork — `tools/decoration-probe/`

The generator's trial overrides (`--padding`, `--radius`, `--peak`, `--arc`) were
documented but silently produced identical output, because the geometry globals
were captured from `PARAMS` at import. `refresh_geometry()` re-derives them after
parsing, and the padding/radius guard now runs on every refresh, so an override
cannot emit a frame the committed artwork would be rejected for. A trial radius
is what proved the ceiling: at the default 6px border, `--radius` above 17 puts
the client's square corner over the frame-line band and is rejected.

Two more captures of the same bug survived that first fix and were only exposed
when the window radius moved from 15px to 10px: the slice table (`LAYOUT`) and the
corner path table (`SHAPES`) were still module-level literals built at import, so
`--radius 10` produced 10px arcs inside 15px slices — a 5px dead band at the outer
edge that the checker did *not* catch, because it derived the shadow ring from the
slice width it had just read. `LAYOUT` is now filled by `refresh_geometry()`,
`SHAPES` is a function, and the checker asserts the real invariants instead of a
tautology: the slice ring must equal the `PaddingTop` in the sibling `MT*rc`
(the value KWin actually reserves), the frame must be `2*(ring+corner)+centre` by
`ring+header+centre+ring+corner`, and the left/top slices must match the corner
footprint. The command that renders an override is also the check — running it at
a second radius is what found both.

`build-decoration.py --check` regenerates every variant in memory and fails when
`decoration.svg` differs, so the SVG cannot be hand-edited out of sync with
`PARAMS`. `check-decoration.py` rasterises each of the nine slices through Qt's
own qsvg plugin, re-stitches the frame and asserts the invariants that have
broken twice: monotonic shadow ramp along every edge, shadow present in all four
corner cutouts, no double-composited ring, the border running continuously round
each corner (mean ≥ 0.90, min ≥ 0.70 coverage), that the drawn band stays 1px wide, that every corner group carries exactly one reinforcement path no wider than 1px, expected fills, no title divider
row. `make check-dpr2` renders the `--arc 1.0` configuration that 2x displays
want, so the 1x compensation is covered in both directions. `--arc` is an absolute
stroke width: `frame_line_arc = 2.0` means a **1px stroke on the same 1px band**, a
second coverage pass rather than a wider line. Passing `--arc 1.0` renders the
*unreinforced* corner the HiDPI case must also survive, and `--arc 3.0` reproduces
the 2px band that shipped once and is now rejected.

The five button SVGs (`close`, `minimize`, `maximize`, `restore`, `menu`) are
generated from the same per-variant palette as the decoration, so `frame_line`
is an explicit token in each `VARIANTS` row rather than a value baked at
import. `tools/decoration-probe/check-buttons.py` independently parses all 20
button files, asserts each of their eight state groups paints exactly the
variant's tones (and no stray colour), and measures real contrast: active and
pressed text ≥ 4.5:1, inactive glyph and the hover-inactive ring ≥ 3:1 against
the variant's own header. It fingerprints every path, rect and stroke width
against Nightshift to prove the five variants share one geometry, and it
cross-checks each generator token against the shipped `.colors` role (Header,
Header[Inactive] and Selection), so a scheme retune cannot leave the artwork on
the old tones. `frame_line` is exempt because it is a documented derivation, not
a scheme role, and the baked inactive glyph is the active Header group's
`ForegroundInactive` — `[Colors:Header][Inactive] ForegroundNormal` is the dimmed
window title, a different role. The hover-inactive ring is `ForegroundInactive`,
not the whisper `frame_line`: the old ring measured 1.02–1.46:1 on the surfaces
it sits on, while the shipped
tone measures 6.33 (Nightshift), 4.99 (Dayshift), 9.25 (Nord Night), 5.46
(Nord Day) and 7.73 (One Dark Pro). Both `check-buttons.py` and all five
`check-decoration.py` runs are wired into `make check`.

## Application style — `tools/style-probe/`

`render-fields.cpp` builds the shipped plugin and renders the whole field family,
the item-view pills, the focus ring, the capacity meter and a scrollbar offscreen,
then `check-style.py` measures the PNGs: corner taper proportional to height,
Breeze's frame suppressed over the pill, 1px focus ring, disabled tone step plus a
dimmed hairline, inset pills with the accent fill, the pill ring, the free-space
meter not a black slab, and a 12px scrollbar gutter.

The family is rendered once per scheme — all five, into
`build/style-probe/out-<scheme>` — because the style is palette-driven.
`check-style.py --scheme <name>` is required and selects that scheme's reference
`window`, pill-text and accent tones; an unknown name exits 2 instead of
silently grading a render with the wrong palette. The former `--light` pass,
which skipped the item hover/inactive ink checks, is gone: those checks now run
on every scheme and use a per-variant `window_rgb` (the *View Base* tone the
grabbed list actually paints) so the light and Nord passes cannot pass
vacuously. CI passes `--ci`, which skips the two assertions that need Breeze
installed (frame suppression, 12px clamp).

**Menu corners (2026-11-17).** The probe also renders a `QMenu` into `menu.png`
(69x100 at this Qt build), asserts the dimension range (60-80 x 90-110) and
measures all four corners by mirroring each into the top-left position; each
corner needs at least 8px recession. The Breeze-only surface measures 2px and
fails, the owned surface measures 12px on all four corners and passes. A
synthetic square-cornered render fails all four assertions, confirming the
guard can catch a one-corner regression. This is a pixel measurement of the outer surface only: the offscreen
menu has no selected row, so it cannot prove that a live highlight stays inside
the corner. Live Dolphin captures cover that case below; the plugin must be
installed system-wide (`make style-install`) or the preview launched with
`QT_PLUGIN_PATH` for the change to appear — the build directory alone does not
affect running apps.

**Hover states (2026-11-17, extended 2026-11-18).** `render-fields.cpp` renders a forced `CE_MenuItem` row with `State_Selected | State_Active` — the state QMenu actually sets on its current row — plus tool-button hover/pressed/checked surfaces, a tool-idle baseline and a `CC_ToolButton` render with `HasMenu` to guard the popup arrow. The owned pills measure 10px (menu row) and 12px (tool buttons) corner recession against Breeze's 2px idle surface. The menu render also asserts that pixels matching the scheme's `pill_text_rgb` survive inside the accent pill: Nord Night failed at 0 before the palette swap and measures 62–113 on the five schemes after it. The idle tool render keeps Breeze's 2px taper, and the arrow render differs from idle by 28–32 pixels at the right edge.

The 2026-11-18 pass adds explicit QQC2 Desktop Style routing probes: `PE_PanelItemViewRow` hover/idle and `CE_ItemViewItem` hover. The hover paths measure 4px inset and 9px corner taper on all five schemes, matching the Qt Widgets item-view path, while idle rows stay unpainted. These are the primitives used by QQC2 Desktop Style `StyleItem` elements `itemrow` and `item`, so Kirigami delegate/list backgrounds can inherit the sculpted pill without a QML override. Kirigami-owned `Menu`, `Popup`, combo-popup, search-popup and inline-message surfaces use `Kirigami.Units.cornerRadius` and remain outside this QStyle plugin's scope; no global radius config is confirmed for Plasma 6.8. Live screenshots of these states were blocked by this host's auto-lock, which kept a dimmed lock layer active after unlock attempts; the forced-state renders are the evidence, and the outer menu corners remain covered by earlier live captures.

**Selected-item active state (2026-11-17).** Dolphin's Places delegate passes
`State_Selected` **without** `State_Active` on its selected row, while the option's
palette group is `Active` — measured live with temporary instrumentation in the
style plugin (`state=0x8001 active=0 paletteGroup=0`, where 0 is `QPalette::Active`).
The pill fill and colour-group helpers previously keyed only off `State_Active`, so
the active row painted the muted inactive grey until further interaction changed the
state. Both helpers now treat an `Active` palette group as active too. The probe
renders `item-selected-palette-active.png` (Selected, no State_Active, Active palette)
and asserts the accent fill; RED was "no accent fill", GREEN on all five schemes.
A genuine inactive row uses `item-selected-inactive.png` with the palette group set
to Inactive and stays muted. Live: `/tmp/opencode/accent-fix-dolphin.png` shows the
blue accent pill on Home on first open, with no clicking (this session's
`AccentColor` override tints it `(31,77,107)`, but the active/inactive distinction
is the fix).

**Tab bars and status strip (2026-11-17).** `CE_TabBarTabShape` and
`PE_PanelStatusBar` are owned by the proxy style; labels and status text stay with
Breeze. A scratch instrumented build confirmed Dolphin asks `PE_PanelStatusBar`
13 times, so the strip is style-reachable after all. Forced renders
(`tab-active.png`, `tab-inactive.png`, `statusbar.png`) fail on Breeze at 2px/0px
and pass at 11px corner recession across all five schemes. Label survival is
proved by rendering each tab twice — shape only and shape plus label — and
counting pixels that differ (229–245 across the schemes), rather than by counting
opaque pixels, which would pass on a label-less fill. A synthetic label-less
render fails that assertion (0 px), proving it can catch the regression. The
inactive fill's dominant tone is asserted to differ from the scheme accent.
Multi-tab seams are a deliberate card-tab look: each tab is an individual rounded
surface, verified by the `tab-multi.png` probe and live
`/tmp/opencode/tab-multi-live.png` (two Kate tabs). Live previews with the built
plugin through `QT_PLUGIN_PATH`: `/tmp/opencode/tab-kate.png` shows the rounded
active Welcome tab, and `/tmp/opencode/tab-dolphin.png` shows the rounded status
strip.

## On-pill ink and interaction steps — `tools/style-probe/check-style.py`

Four defects here were invisible in a review and measurable in the renders:

- **On-pill ink.** A selected tab sits on the accent fill, so its label must take
  `HighlightedText`. The check takes the pill's surface tone and the
  strongest-contrast pixel as the painted ink, then asserts **both** that the ink
  matches `HighlightedText` from the scheme and that it clears 4.66:1 — contrast
  alone would accept any bright pixel, and ink alone would accept an unreadable
  one. The muted tab of an inactive window is asserted the other way round: it
  must still be `WindowText`, because `HighlightedText` there is white on light
  grey. Proven by removing the `CE_TabBarTabLabel` interception: the render drops
  to 3.00:1 with `WindowText` ink and fails.
- **Checked tool buttons and their icons.** A toolkit icon cannot be recoloured
  from a style option, so the pill — not the ink — has to carry the contrast. The
  probe renders a checked button with an icon filled in the theme's own ink and
  requires 3:1 for the icon and 4.66:1 for the label. With the old saturated
  accent fill both measure 2.23:1 on Nord Night and fail; the tonal fill measures
  5.04–9.85:1 across the five variants.
- **Tab steps.** Idle keeps the 7% tone and hover is 13%, so the two must
  differ by at least 6/255 — the flat single tone that shipped made idle and
  hovered identical. Idle is separately held to a 12/255 floor above the page
  tone, because a first attempt at 3% left tabs reading as floating labels.
- **Tooltip tier.** `PE_PanelTipLabel` had no probe coverage at all. The render is
  now asserted twice: its corner taper must sit in the 10px band (5–9px, measured
  8px; at the old 6px it measures 4px and fails) and its fill must equal the
  scheme's `Colors:Tooltip/BackgroundNormal`.
- **Separator inset.** The forced `CE_MenuItem` separator render must be exactly
  one row, spanning 8px inside each edge of a 120px canvas. With the inset set to
  zero it spans 0–119 and fails.
- **Disabled tool button.** A disabled checked button must never paint the accent
  fill; the check compares its dominant tone against the scheme accent.

Two further measurements ride on the same renders: the meter label must clear
3:1 on both the fill and the groove side, and the check mark's bounding box must
stay inside the inner 60% of the chip.

## Plasma Style assets

`make check` validates every SVG as XML, the metadata as JSON, and reads the
shipped corner paths directly: panel and dialog frames must be 6px, the popup
frame 14px, in every variant. A regenerated sample is no longer measured, so a
file that drifted from its documentation fails instead of passing. The three lookup slots of each owned surface must hash-match, which
`design.md` §10 records as the one-hash rule.

Two generators own the frame geometry, and both `--check` runs are in
`make check`:

Both generators now cover **all five variants × three slots** (15 files each). They
previously emitted only Nightshift and Dayshift, so the other three variants were
unguarded copies that could drift silently; because the assets are palette-driven
class geometry, the generated output is byte-identical for every variant.
`check-style.py` additionally measures the shipped corner path of all three frame
assets in every variant, so the files and this documentation cannot disagree.

- `tools/plasma-theme/dialog-frame.py` builds `dialogs/background` from Breeze's
  solid slice set verbatim, adds the 1px band on the four strips and takes the
  four corner bodies from the tooltip, so dialogs, menus and tooltips share one
  6px construction. It also asserts that each corner's artwork spans exactly the
  border it is stretched into.
- `tools/plasma-theme/applet-background.py` builds `widgets/background` — the
  frame behind every Plasma popup — at **14px**, keeping Breeze's 14px content
  insets and carrying its `shadow-*` slices through, with the same
  corner-span assertion.

Both guard defects that actually shipped: a Frame band drawn as a chord instead of
an annulus (a diagonal seam across each corner), and corner artwork smaller than
its border, which KSvg stretches into a distorted arc with a band three times too
thick. A corner that does not span its border is the failure mode to look for when
a popup's corners look "nearly right but not quite".

## Live session — `make verify-live`

The offline suite describes files; these values only exist in the running session.
`make verify-live` reads them through the same variant table as `make apply`, so
one command covers every installed look:

| Value | Expected |
| --- | --- |
| `[KDE] frameContrast` in `kdeglobals` | `0.05` — `plasma-apply-lookandfeel` resets it to the stock 0.2 on every run, which triples the strength of every derived seam |
| Installed scheme, Plasma Style, Aurorae files | byte-identical to the repo, for **all five** variants |
| `/usr/lib64/qt6/plugins/styles/mtnightshiftstyle.so` | byte-identical to `build/style/mtnightshiftstyle.so` |

The three selection values are per variant (the Look-and-Feel id is derived from
the style id, `com.mayanktaker.<style>.desktop`):

| `make verify-live` variant | `[General] ColorScheme` | `[Theme] name` | decoration |
| --- | --- | --- | --- |
| `nightshift` (default) | `MT-Nightshift` | `mt-nightshift` | `__aurorae__svg__MTNightshift` |
| `dayshift` | `MT-Dayshift` | `mt-dayshift` | `__aurorae__svg__MTDayshift` |
| `nord-night` | `MT-Nord-Night` | `mt-nord-night` | `__aurorae__svg__MTNordNight` |
| `nord-day` | `MT-Nord-Day` | `mt-nord-day` | `__aurorae__svg__MTNordDay` |
| `one-dark-pro` | `MT-One-Dark-Pro` | `mt-one-dark-pro` | `__aurorae__svg__MTOneDarkPro` |

A session that fails one of these renders the previous build indefinitely — the
failure mode that hid a stale 1.2.0 Plasma Style and an un-updated 1.3.0 plugin.

The old `DAYSHIFT=1` switch is inert: `make verify-live VARIANT=dayshift` checks
the light selection, `VARIANT=nord-night` / `VARIANT=nord-day` check the two
Nord selections, and `VARIANT=one-dark-pro` checks the fifth. `make apply
VARIANT=<name>` installs and selects any of the five (`make apply-dayshift` and
its Nord / One Dark Pro aliases are thin wrappers over the same variable).
Running the check against a variant that is not active is the best
self-test: it names every mismatch rather than reporting a bare failure. On
2026-11-16 the four original variants were applied and verified live in turn;
the Nord captures are `/tmp/opencode/nord-night.png` and
`/tmp/opencode/nord-day.png`. On 2026-11-17 `make apply VARIANT=one-dark-pro`
and `make verify-live VARIANT=one-dark-pro` both reported a matching session.
The desktop was captured on a bright wallpaper
(`/tmp/opencode/one-dark-pro-light.png`, plus the maximized
`/tmp/opencode/one-dark-pro-maximized-light.png`) and on the dark DarkestHour
wallpaper (`/tmp/opencode/one-dark-pro-dark.png`): the One Dark Pro titlebar
buttons (minimize / maximize / close) and the 1px frame line stay legible on
both, and the header/frame fill reads `#282C34` against both backgrounds.
The session was then returned to the canonical `nightshift` baseline and plain
`make verify-live` passed. This Wayland host has two 1920×1080 outputs and no
pointer-injection tool; windows were driven through KWin global shortcuts over
DBus and captured with `spectacle -b -n -o`. A wallpaper switch was needed for
the light-background review (the stock wallpaper's dark regions hid the frame),
and the original per-output wallpapers were restored byte-for-byte from a
backup of `plasma-org.kde.plasma.desktop-appletsrc`.

One session-level limit: Plasma's `[General] AccentColor` preference overrides
the `Selection` palette group for Qt Widgets. In the captured session it is
`33,98,138`, so a live selected pill renders as its 80% derivative `33,80,111`
rather than the scheme's own `Selection.BackgroundNormal`; reapplying
`plasma-apply-colorscheme` while the scheme is already active does not rewrite
the group. The lighter Nord Night alternate therefore has to be checked from the
palette and the offscreen probe, not from a live selection in that session.

## What this cannot see

- **Running processes.** `make verify-live` proves the files and config values, not
  that an app which is already open reloaded them: a Qt style is resolved once per
  process, and KWin caches decoration paths and `Padding*` for the life of the
  compositor. Relaunch the app (and, for a decoration change, KWin) to see the new
  build.
- **The full panel SVG.** qsvg aborts on the complete `panel-background.svgz`,
  which is why the corner radius is measured on a generated sample rather than
  the shipped file.
- **Colour judgement.** Ratios are necessary, not sufficient: the artwork must
  also be reviewed on a light wallpaper as well as a dark one, because a bright
  background exposes doubled shadow bands and wrong strips that a dark one hides.
