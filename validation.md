© Mayanktaker Computers & Web Development | https://mayanktaker.com

# Validation

How every claim in `design.md` is measured, and what the suite cannot see. One
concern: verification. Visual decisions live in `design.md`; scope and task
state live in `PLAN.md`.

## One entry point

```bash
make check        # decoration drift + raster invariants, palette/metadata audit, style probe (dark and light)
make check-dpr2   # the same artwork rendered at 2x, where the corner arc is 1px
make verify-live  # the running session: config values, deployed copies, system plugin
```

`make check` and `make check-dpr2` run in CI (`.github/workflows/checks.yml`) on
every push and pull request; `tools/git-hooks/pre-commit` runs the palette audit on
every commit and the decoration checks whenever Aurorae artwork is staged.
`make verify-live` needs a session, so it runs after `make apply` instead.

The probe's `--ci` flag is passed only when `GITHUB_ACTIONS` is set, because CI
has no Breeze style. A shell that merely exports `CI=true` still runs the full
assertions, which is the safe default: the two skipped checks are exactly the
ones a local machine can prove.

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

The Nord schemes keep the design's canonical tones wherever they clear the
floors. `Selection.BackgroundAlternate` was adjusted in both variants, because
plain nord10 `#5E81AC` left dark pill text at 3.10:1 on Night and white pill
text at 4.03:1 on Day; the alternates are now `#93B3D1` (Night, lighter than the
pill) and `#405A79` (Day, deeper). Semantic tones were also tuned where the
canonical value missed: Night lifted negative, positive, active, link and
visited; Day deepened negative, active, link and visited. Every other tone is
the design's first pass verbatim.

## Decoration artwork — `tools/decoration-probe/`

`build-decoration.py --check` regenerates every variant in memory and fails when
`decoration.svg` differs, so the SVG cannot be hand-edited out of sync with
`PARAMS`. `check-decoration.py` rasterises each of the nine slices through Qt's
own qsvg plugin, re-stitches the frame and asserts the invariants that have
broken twice: monotonic shadow ramp along every edge, shadow present in all four
corner cutouts, no double-composited ring, the border running continuously round
each corner (mean ≥ 0.75, min ≥ 0.45 coverage), expected fills, no title divider
row. `make check-dpr2` renders the `--arc 1.0` configuration that 2x displays
want, so the 1x compensation is covered in both directions.

## Application style — `tools/style-probe/`

`render-fields.cpp` builds the shipped plugin and renders the whole field family,
the item-view pills, the focus ring, the capacity meter and a scrollbar offscreen,
then `check-style.py` measures the PNGs: corner taper proportional to height,
Breeze's frame suppressed over the pill, 1px focus ring, disabled tone step plus a
dimmed hairline, inset pills with the accent fill, the pill ring, the free-space
meter not a black slab, and a 12px scrollbar gutter.

The family is rendered twice — once under each scheme — because the style is
palette-driven. The light pass runs the palette-agnostic assertions only
(`--light`): the item hover/inactive checks measure ink against the dark `Window`
tone and would pass vacuously on a light render. CI passes `--ci`, which skips the
two assertions that need Breeze installed (frame suppression, 12px clamp).

## Plasma Style assets

`make check` validates every SVG as XML, the metadata as JSON, and the panel
background's corner radius by sampling the regenerated probe SVG (14px
recession). The three lookup slots of each owned surface must hash-match, which
`design.md` §10 records as the one-hash rule.

Two generators own the frame geometry, and both `--check` runs are in
`make check`:

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

The offline suite describes files; these values only exist in the running session:

| Value | Expected |
| --- | --- |
| `[KDE] frameContrast` in `kdeglobals` | `0.05` — `plasma-apply-lookandfeel` resets it to the stock 0.2 on every run, which triples the strength of every derived seam |
| `[General] ColorScheme` | `MT-Nightshift` |
| `[Theme] name` in `plasmarc` | `mt-nightshift` |
| `[org.kde.kdecoration2] theme` | `__aurorae__svg__MTNightshift` |
| Installed scheme, Plasma Style, Aurorae files | byte-identical to the repo |
| `/usr/lib64/qt6/plugins/styles/mtnightshiftstyle.so` | byte-identical to `build/style/mtnightshiftstyle.so` |

A session that fails one of these renders the previous build indefinitely — the
failure mode that hid a stale 1.2.0 Plasma Style and an un-updated 1.3.0 plugin.

`DAYSHIFT=1` checks the light selection instead (`make apply-dayshift` runs it
that way). Running it against the other variant is the best self-test: it names
every mismatch rather than reporting a bare failure.

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
