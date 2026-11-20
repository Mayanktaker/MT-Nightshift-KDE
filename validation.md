© Mayanktaker Computers & Web Development | https://mayanktaker.com

# Validation

How every claim in the design docs is measured, and — just as important — what the
suite **cannot** see. One concern: verification.

| Document | Covers |
|---|---|
| **[validation-tools.md](validation-tools.md)** | The offscreen probes: package/palette audit, Aurorae artwork, the Qt style probe, the Plasma Style assets |
| This file | The live session (`make verify-live`), the two manual spot-checks, and the suite's blind spots |


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

## Live spot-checks — the two that need a hand

Everything these confirm is also asserted offscreen, so they are a spot-check on the
composited result rather than the only evidence. Each takes seconds; what follows is
the procedure, so it is not rediscovered per session.

**1. Panel context menu and a tooltip.** Right-click empty space on the panel, then
hover a task-manager entry to raise its tooltip. Expected, from `design.md` §6 and
`application-style.md`:

| Surface | Radius | Check |
|---|---|---|
| QMenu (the context menu) | 15px | The four outer corners are visibly rounder than a menu row's own pill, and the 1px hairline follows the arc |
| Menu row hover | 10px | The hover pill clears the corner rather than filling it |
| Menu separator | inset 8px | The hairline does not reach either menu edge |
| Tooltip | 10px | Not the sharpest rectangle on screen |

**2. Dolphin path-bar focus ring.** Click into Dolphin's path bar so it becomes editable
(`Control` → *Editable Location*, or `Ctrl+L` **by hand** — injected keys do not reach
focused clients). Expected: a 1px accent ring around the `Base`-toned pill, with the
text and the icon clear of the corners. `check-style.py` asserts the same ring offscreen
at 1px on all five schemes, so this only confirms that the composited result matches.

**Why they are not automated.** Pointer injection lands but drifts by several pixels,
which is enough to miss a 24px menu button; and injected keystrokes reach KWin's global
shortcuts but are dropped by focused clients, so `Ctrl+L` cannot be synthesised. A
screenshot-based radius measurement was prototyped and discarded: on an antialiased
capture with a shadow ring the estimate carried a systematic bias larger than the
difference between the 10px and 15px artwork it was meant to distinguish.

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
