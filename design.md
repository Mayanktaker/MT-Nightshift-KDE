© Mayanktaker Computers & Web Development | https://mayanktaker.com

# MT Nightshift — design specification

The visual source of truth for this project. `PLAN.md` holds scope and task state, `AGENTS.md` holds the compact project map, `README.md` holds provenance and licensing.

## 1. Direction

**Nightshift OLED.** A dark Plasma desktop built for long evening sessions on an OLED panel: carbon surfaces that sit just above true black, blue used only where it means *active*, and edges that are drawn rather than blurred.

Three rules drive every decision:

1. **Not black, but close.** No surface is `#000000`. The deepest content area is `#0A0B0D`, so text never floats on a void and OLED pixels still switch off almost fully.
2. **Blue is a signal, not decoration.** Breeze blue appears on focus rings, active indicators, selection fills and links. Panels, dialogs, menus and controls stay neutral carbon.
3. **Edges are explicit.** The three owned shell surfaces use a 1px frame line and Breeze's tight shadow. They stay opaque and gradient-free; inherited control artwork keeps Breeze's small built-in shading where it communicates state.

Breeze geometry is kept deliberately: same 6px frame radius, same 4px content inset, same frame-slice structure. The theme should read as *stock Plasma, turned down*, not as a reskin.

## 2. Palette

Values are sRGB hex, taken from `color-schemes/MT-Nightshift.colors`. Contrast figures are WCAG 2.1 ratios measured against the surface named in the "on" column.

### Surfaces

| Role | Hex | L\* | Used for |
| --- | --- | --- | --- |
| `View` background | `#0A0B0D` | 3.0 | text areas, list and tree views, scroll areas, search results |
| `View` alternate | `#0A0B0D` | 3.0 | unified with the row background: no zebra stripe, so list rows never step brighter than the well they sit in |
| `Window` background | `#101216` | 5.4 | panels, dialogs, menus, popups, OSD — the base "carbon" surface |
| `Window` alternate | `#171A1F` | 9.2 | secondary window areas, grouped sections |
| `Header` background | `#15181C` | 8.1 | title areas, toolbars, header rows (a tab strip is *not* here — `QTabBar` sits in the client area, so tabs derive from `Window`) |
| `Header` alternate | `#101216` | 5.4 | strip behind a toolbar, inactive header |
| `Button` background | `#1B1F25` | 11.6 | buttons, comboboxes, spinboxes, pressed controls |
| `Button` alternate | `#12303F` | 18.4 | accent-tinted button/alternate fill (Breeze parity slot) |
| `Tooltip` background | `#21252C` | 14.6 | tooltips, "what's this" popups, hover cards |
| `Tooltip` alternate | `#262B33` | 17.4 | tooltip heading strip |
| `Complementary` background | `#0D0F13` | 4.3 | side panels, docked tool views, complementary areas |
| `Selection` background | `#1F6E9C` | 44.0 | selected rows, active list items, pressed toolbar buttons |
| `Selection` alternate | `#174E70` | 31.3 | selected row behind other selected rows, selection hover |

The ladder steps are 2.4–3.5 L\* apart, so neighbouring layers separate by tone alone before a border is drawn. Nothing reaches pure black; the darkest value still has a measurable blue-grey cast (`R<G<B`), which keeps the neutral family consistent with Breeze's `#232629`.

### Text

| Role | Hex | On `Window` | Worst case in its own group | Used for |
| --- | --- | --- | --- | --- |
| Normal | `#E8EBF0` | 15.7:1 | 11.9:1 (`Tooltip` alternate) | body text, labels, titles |
| Inactive | `#8D97A4` | 6.3:1 | 4.67:1 (`Button` alternate) | secondary labels, hints, placeholders |
| Active | `#4FB4E6` | 8.0:1 | 5.9:1 (`Button` alternate) | active window/active-state text |
| Link | `#4AA5EA` | 7.0:1 | 5.2:1 (`Button` alternate) | hyperlinks |
| Visited | `#BB86DC` | 6.7:1 | 5.0:1 (`Button` alternate) | visited links |
| Negative | `#D08084` | 6.3:1 | 4.67:1 (`Button` alternate) | errors, destructive actions |
| Neutral | `#F0A32B` | 8.9:1 | 6.6:1 (`Button` alternate) | warnings, "needs attention" |
| Positive | `#4BC97A` | 8.9:1 | 6.5:1 (`Button` alternate) | success, connected, done |

Normal text is `#E8EBF0` rather than `#FFFFFF`: at these background levels white is a light source on an OLED panel, and the 15:1 ratio is already beyond comfortable.

**How these numbers are measured.** Every `Foreground*` role is checked twice: against the `BackgroundNormal` *and* the `BackgroundAlternate` of the group that owns it, because rows, strips and raised controls do use the alternate. That is eight groups (`Button`, `Complementary`, `Header`, `Header[Inactive]`, `Selection`, `Tooltip`, `View`, `Window`) × eight roles = 64 checks, each measured against two backgrounds, so 128 measurements. Ratios use the WCAG 2.1 relative-luminance formula on sRGB values, with no rounding inside the calculation. The lowest ratio in the palette is **4.66:1** (`Selection` positive on `#1F6E9C`); the lowest outside the selection fill is 4.67:1 (`ForegroundInactive` on the alternate surfaces). `#D08084` is the dimmest red that still clears the floor: the 2026-11 dimming pass shipped `#CE7074` for calmer capacity meters and error text, which measured 4.07:1 on the `Button`/`Complementary` alternate `#12303F` and 4.20:1 on the tooltip alternate `#262B33` — below AA. The shipped value keeps that muted reading (38% saturation, against 46% for the dimmed red and 52% for the earlier pastel) and is lifted only as far as the floor requires: 4.67:1 on the worst surface, 6.34:1 on `Window`, hue unchanged.

**Inside a selection fill** the foregrounds are near-white tints rather than saturated colours, because `#1F6E9C` is a mid-luminance surface: a red or green dark enough to read as a hue cannot also reach 4.5:1 against it. Hue still carries the meaning: inactive `#E6EDF2` (4.71:1), link `#DCEEFF` (4.70:1), visited `#F2E9FA` (4.73:1), negative `#FFE6E8` (4.71:1), neutral `#FFE9C5` (4.70:1), positive `#C9F5DA` (4.66:1), all measured against the fill itself.

### Accents

| Role | Hex | Contrast on `Window` | Used for |
| --- | --- | --- | --- |
| Focus / `DecorationFocus` | `#3496C9` | 5.7:1 | keyboard focus outlines, focused controls, and the fill Breeze's list artwork uses for selected and hovered rows |
| Hover / `DecorationHover` | `#2A7FA8` | 4.2:1 | hover outlines and indicators |
| Selection fill | `#1F6E9C` | 3.4:1 vs `Window` | selected rows, active toggles, checked controls |
| Selection text | `#FFFFFF` | 5.6:1 on selection | text inside a selection fill |
| Active text | `#4FB4E6` | 8.0:1 | active-state labels, not used as a fill |

Hover and focus share one hue but differ in strength: hover is quiet, focus is unmistakable. This is the one place the theme departs from Breeze, which uses the same blue for both — a single unvarying accent makes keyboard focus hard to find on a near-black desktop.

Both tokens carry more weight than their names suggest, because Breeze's list artwork paints *fills* with them: `viewitem` uses `ButtonFocus` for a selected row's pill, `listitem` uses `ViewFocus` for pressed and hovered rows. A selected row is therefore 80% focus blue over the row background, and white text sits on it. That is why focus is `#3496C9` and not the brightest blue: composited that way it lands at `#2D7CA5`, which keeps white text at 4.6:1, still 5.7:1 against a panel. `#4FB4E6` is kept for active text, where it never covers an area.

The selection fill is a deeper Breeze blue (`#1F6E9C`, hue 202°) instead of Breeze's `#3DAEE9`. Full-strength Breeze blue fills glow on an OLED panel and force a contrast compromise against white text. The deeper fill keeps 5.6:1 with white text and still reads as the same blue family.

## 3. Surface rules

- **One surface colour per layer.** A panel is `Window`, its menus are `Window` plus a frame line, tooltips are `Tooltip`. No layer is a translucent tint of another.
- **Opaque.** Three surfaces (panel, tooltip/menu popup, dialog popup) are overridden so they paint at full opacity instead of Breeze's 85%, and each is shipped at every lookup slot Plasma can request so no path can quietly fall back to stock Breeze art (see §7). Nothing in the theme depends on what is behind it.
- **Ordered by importance, not by z-order.** Content wells are darkest (`View`), chrome is lighter (`Window`), controls lighter again (`Button`), and anything that must be read *over* something else is lightest (`Tooltip`).
- **Selection is a fill, not a tint.** Selected content uses the selection blue at full strength with white text; hovered content uses the hover blue as an outline only.

## 4. Interaction states

| State | Colour source | Appearance |
| --- | --- | --- |
| Rest | `Button` / `View` background | flat carbon, 1px frame line |
| Hover | `DecorationHover` `#2A7FA8` | 1px outline on the control, no fill change |
| Focus | `DecorationFocus` `#3496C9` | 1px ring, brighter than hover; always visible regardless of input device |
| Pressed | `Selection` `#1F6E9C` at full strength, or `Selection` blended 55% toward the window tone for toolbar buttons (`kToolStateTint`) | fill only; geometry never moves |
| Selected | `Selection` `#1F6E9C` + `#FFFFFF` text | fill only; Breeze's own selected-row artwork uses the focus blue, which is why that token stays dark enough for white text (see §2) |
| Disabled | `ColorEffects:Disabled` (Breeze values) | desaturated, contrast reduced; no custom colour |
| Active window / inactive window | `Header`, `Header[Inactive]` | active header is `#15181C`; inactive header drops to `#101216` with dimmed title text |

Rules: state changes never move or resize a control; a state is always readable without colour alone (focus adds an outline, selection changes the fill, pressed changes the fill); inactive windows are not dimmed by an overlay — the theme keeps Breeze's `ColorEffects:Inactive` disabled so text stays legible.

## 5. Typography

Plasma Style assets do not carry fonts, and this theme deliberately does not override them.

- **Family:** the system UI font, unchanged (Noto Sans on Fedora KDE). No font keys are shipped in `plasmarc`, `metadata.json` or the colour scheme.
- **Hierarchy** comes from the platform's own scale: `Small` for metadata and hints, `Normal` for body and labels, `Large` for dialog headings and OSD numerals, `Bold` only for section headings and the focused item in a list.
- **Numbers** are left to the font's tabular figures, as Breeze does; the theme ships no numeric-specific sizes.
- **Never** ship a custom font in a Plasma Style: it cannot be loaded from the theme directory and would silently fall back.

## 6. Shape, spacing, depth

- **Radius scales with the surface, up to a ceiling.** A corner is read relative to the shape that carries it: 10px is very round on a 32px button and subtle on a 1920px window. The theme has three tiers — **popups 14–15px** (QMenu 15, applet popup 14), **controls and windows 10px**, and **chips 4–5px** — with one invariant: *a container is never sharper than the contents it holds.* The earlier 6px dialog/panel tier broke that invariant (containers tighter than the 10px controls inside them) and read as an unfinished edge; it is still open for dialogs and panels, tracked in `PLAN.md`. The window was originally 15px and deliberately lowered to **10px** so the outer silhouette matches every control, hover pill and tooltip on screen: at 15px a window was rounder than anything it contained, and the mismatch was the most visible seam left in the suite. The old argument that 10px reads square on a large surface did not survive a live test — the window corner is only ever seen against its own edge, not scaled against the window.
- **Plasma frame geometry stays independent.** The Aurorae window frame now shares the 10px control radius, but the Plasma frame assets keep their existing values; they are not generated by the Qt control-radius rule. The applet/popup background (`widgets/background`) is the **14px** surface. Full-window dialogs and the panel frame still ship Breeze's `6px` band with a `32×32` centre: raising them is a real geometry change (new corner bodies, not a slice resize), and the two earlier attempts both shipped visible defects — a band drawn as a chord across the corner, then a corner smaller than its border that KSvg stretched. That tier stays at 6px until the corner bodies can be regenerated and reviewed live; it is tracked in `PLAN.md`, not silently accepted.
- **Qt control surfaces share one radius.** Fields, buttons, tabs, check chips, progress meters, menu rows, item-view rows, tooltips and their hover/pressed/focus surfaces use a **10px maximum radius**, clamped to fit smaller controls. A `QMenu` — including Dolphin's hamburger menu and every submenu — keeps its existing **15px** outer popup radius and 1px `ColorScheme-Frame` hairline. Tooltips joined this tier (6px → 10px): they are painted by the style, and at 6px they were the sharpest rectangle on screen.
- **QQC2 delegate rows follow QStyle.** Kirigami list/sidebar backgrounds that use QQC2 Desktop Style `StyleItem` elements route `itemrow` through `PE_PanelItemViewRow` and `item` through `CE_ItemViewItem`, so their hover and selection pills use the shared 10px control radius. Popup surfaces owned directly by Kirigami/QQC2 (`Menu`, `Popup`, combo popups, inline message bars and search popups) remain KDE-controlled.
- **Applet popups are the 14px case.** `widgets/background` covers the notification history, tray, Kickoff and widget explorer; it keeps Breeze's 14px content insets so popup layout is unchanged.

- **Interaction states follow the surface.** Fields, combos and spin boxes receive a quieter accent outline on hover and a stronger 1px ring on focus. The hover cue is the accent **pulled 45% toward the surface** (`kHoverMute`) before its 3:1 floor is applied; a contrast target alone does not separate the two states, because when the accent already clears the focus target both rings resolve to the identical tone — which is what happened on four of the five schemes. Hovered or keyboard-selected menu rows, hovered/pressed/checked tool buttons and item rows use the same 10px maximum radius and palette-driven state tones; icons and text remain clear of the corners. The QMenu's 15px outer popup surface is unchanged.
- **On-pill ink is a rule, not a special case.** Wherever a text-only surface becomes the accent fill, its label moves to `HighlightedText`: selected menu rows, selected and hovered item rows, pressed or checked push buttons and selected tabs. A selected tab label painted in `WindowText` measured 1.52–2.65:1 on One Dark Pro, Nord Day, Nord Night and Dayshift; `HighlightedText` puts the same label at 4.86–5.57:1 on all five. **Tool buttons are the exception, and the reason is icons.** Qt draws a `QIcon` from a pre-rendered pixmap and takes no palette from the style option, so an icon's colour is whatever the icon theme baked in — normally the same tone as `WindowText`. A saturated accent pill therefore pushes those icons to 2.23–2.31:1 on Nord Night, Nord Day and One Dark Pro (text could be recoloured, the icon could not). A pressed or checked tool button instead takes a **tonal fill** — the accent blended 55% towards the window tone — which lifts text *and* icon to 5.04–9.85:1 on all five while still reading as a blue-tinted "on" state. The distinction is deliberate: surfaces whose content the style controls take the accent; surfaces whose content it does not take the tint.
- **Tabs have three distinguishable steps.** Idle keeps the 7% `Window`→`WindowText` step the flat implementation used — painted rather than delegated, so Breeze's tighter corner cannot return — hover rises to 13%, and the selected tab is the accent fill. The earlier design used that 7% for every state, so idle and hovered were pixel-identical and hover gave no feedback at all. Idle must stay at the 7% level: dropping it to 3% left tabs 5–7/255 above the page, where they read as floating labels rather than tabs, so `check-style.py` now asserts a 12/255 floor against the page tone.
- **Menu separators are inset.** A separator is a 1px hairline at 14% contrast, inset 8px from both menu edges. Drawn edge to edge it cut across the 15px menu corner and read as a stray border. The group-break rule therefore matches the 4px inset rhythm of the row pills, scaled for a menu surface.
- **Meter labels split their ink.** `CE_ProgressBar` text can straddle the fill boundary, where no single colour clears the floor on both the accent fill and the groove. The label is drawn twice with clipping: `HighlightedText` inside the fill, `Text` outside it (5.57:1 and 11.46:1 on Nightshift). A meter with no fill keeps the groove ink across its whole width, and `check-style.py` reads the fill's right edge out of the render rather than assuming it, so the two sides can never be measured on the wrong side of the boundary.

- **Check and radio chips belong to the field family.** Qt Widgets and QQC2-rendered check boxes share rows with fields, so `PE_IndicatorCheckBox` and `PE_IndicatorRadioButton` take the **Button** tone with a quiet 7% hairline and a corner proportional to the 10px control radius (up to **5px** on a 20px chip; radios remain circular). The mark itself keeps a fifth of the chip clear on every side — an earlier 26–76% span put the stroke against the corner cut and read cramped at 20px. Keyboard focus draws the accent ring on the chip itself; the item-view focus pill is restricted to `QAbstractItemView`, so a focused label is never wrapped in a capsule. Disabled chips step halfway back to the page tone instead of lifting, which keeps enabled and disabled states distinct in both polarities.

- **Tab bars and status strips join the language.** Qt tab shapes and `PE_PanelStatusBar` are painted by the style proxy with the same clamped radius; their text and labels stay with Breeze. Plasma QML panels remain outside this reach.
- **Content inset 4px** (`hint-*-margin`) for panels, dialogs and tooltips — Breeze's value. Text sits 4px inside a panel edge; controls add their own padding on top. Applet popups keep their **14px** inset, which is what Breeze's current widgets are laid out for; the generator preserves it while changing only the radius.
- **Panels** keep Breeze's 6px margins, so panel thickness and widget spacing are unchanged.
- **Edge treatment:** a 1px `ColorScheme-Frame` line on the outer contour of the frame assets this theme ships, inside the surface. KDE derives that colour as a mix of the `Window` background and text, tuned by `[KDE] frameContrast`, so the edge stays in family if the palette is retuned.
- **Shadow:** Breeze's existing cast shadow is kept, unmodified. It provides separation from the wallpaper; it is not part of the surface.
- **Owned shell surfaces have no gradients, translucency, glow, or inner highlight bevel.** The Breeze "solid" slice set omits Breeze's 50%-alpha inner highlight lines. Inherited button and control artwork retains its original Breeze gradients/shadows for state shading; redrawing those controls is outside this first pass.
- **Blur is switched off** at theme level (`[BlurBehindEffect] enabled=false`), because there is nothing translucent left to blur; a blur behind an already near-black shadow only produces a haze.
- **Adaptive transparency is switched off** (`[AdaptiveTransparency] enabled=false`), because the surfaces are already opaque; adapting them would only add movement.

## 7. Plasma Style asset strategy

Inheritance first, overrides only where the palette cannot reach.

**Inherited from the system Breeze `default` theme** (unchanged, tinted by this theme's `colors`): every widget, control, icon and indicator asset — buttons, line edits, sliders, switches, checkboxes, radiobuttons, scrollbars, tab bars, task manager, pager, clock, calendar, notes, media delegates, margins/highlights, all `icons/*`. These assets reference Breeze `ColorScheme-*` CSS classes, so the Nightshift palette drives them with no file copies.

**Overridden** in `themes/mt-nightshift/` — four surfaces, each shipped at every lookup slot Plasma can ask for. Every copy derives from Breeze's own `solid/` slice set (identical slice names, margins, insets and 6px radius; opaque fills; no translucent inner highlight), with the 1px frame line from §6 added inside the contour.

**Both remaining frame assets are generated, never hand-derived.** The first dialog derivation rebuilt the frame at 14px borders while drawing the Frame band as a chord across each corner: on the notification toast that read as a square corner with a diagonal hairline and a notch (captured 2026-11-15). `tools/plasma-theme/dialog-frame.py` now takes Breeze's `solid/` slice set verbatim, adds the 1px band on the strips and takes the corner bodies from the tooltip, so menus, dialogs and tooltips share one 6px construction by definition. `tools/plasma-theme/applet-background.py` builds the popup frame at 14px with Breeze's insets and shadow slices. Both `--check` runs are part of `make check`.

| Surface | Slots shipped | What asks for it |
| --- | --- | --- |
| panel | `widgets/panel-background`, `solid/widgets/panel-background`, `translucent/widgets/panel-background` | `Panel.qml`: base frame for the adaptive/translucent item, `solid/…` for the opaque and floating-opaque items |
| menu popup, combobox popup, tooltip | `widgets/tooltip`, `solid/widgets/tooltip`, `translucent/widgets/tooltip` | `PlasmaComponents` `Menu.qml` and `ComboBox.qml` (Window colour set) plus `ToolTip.qml` (Tooltip colour set) request `solid/widgets/tooltip` **directly** |
| dialog, popup, OSD heading | `dialogs/background`, `solid/dialogs/background`, `translucent/dialogs/background` | `LockOsd.qml`, `PlasmoidHeading.qml`, `PlasmaCore.Dialog` |
| applet and popup background | `widgets/background`, `solid/widgets/background`, `translucent/widgets/background` | `PlasmaComponents` `Dialog`/`Popup`/`Drawer`, `PlasmaCore.DialogBackground` (every notification, tray and Kickoff popup), `BackgroundMetrics.qml` |

Three facts fix this layout:

1. **Direct requests bypass the base name.** `Menu.qml`, `ComboBox.qml` and `ToolTip.qml` hard-code `imagePath: "solid/widgets/tooltip"`, and `Panel.qml` hard-codes `solid/widgets/panel-background` for opaque panels. A theme that ships only `widgets/tooltip` resolves those requests to `default/solid/…` — stock Breeze artwork, tinted with our palette, but with no 1px edge and Breeze's own slice treatment. Shipping the `solid/` slot is the only way to keep menus, comboboxes, tooltips and opaque panels on the same surface.
2. **The `translucent/` slot is live on Wayland.** Plasma selects `translucent/` whenever `KWindowEffects::isEffectAvailable(BackgroundContrast)` is true — a KWin-side condition that `[BlurBehindEffect] enabled=false` does not influence. Lookup order is `theme/translucent/<path>` → `theme/<path>` → `default/translucent/<path>` → `default/<path>`, so the base copy would still win, and the translucent copies exist to make the answer explicit and keep it correct if a selector path is ever requested directly, exactly as `solid/` is today.
3. **All three copies are byte-identical.** Breeze's base, `solid/` and `translucent/` slices for these surfaces share one hint grid, so a single derivation serves every slot: the theme simply has no translucent variant. Identical output is verified with `sha256` (§10).

`opaque/` is deliberately not shipped. Plasma selects it only when compositing is off (X11 without a compositor), which the Wayland target never does, and `theme/opaque/<path>` falls back to `theme/<path>` in any case.

`widgets/background.svgz` **is** overridden as of the 2026-11 popup pass, reversing the earlier decision. It is the frame behind every Plasma popup — the notification history, the tray, Kickoff, the widget explorer — because `PlasmaComponents` `Dialog`/`Popup`/`Drawer` and `PlasmaCore.DialogBackground` all draw it. Breeze's copy uses a 4px corner inside a 4px border, so next to the theme's 10px Qt controls those popups read as square surfaces with a short nub (captured 2026-11-16). `tools/plasma-theme/applet-background.py` regenerates the nine-slice frame at **14px** with a 1px `ColorScheme-Frame` band, keeps Breeze's **14px content insets** so popup layout does not move, and carries Breeze's `shadow-*` slices through verbatim so popups keep their shadow. Its `--check` runs in `make check`.

Nothing else is copied. If a future Breeze release changes a shared asset, this theme picks it up automatically.

**Derivation and licences.** The four surfaces (twelve files: one per selector slot, each generated) are derived from KDE Breeze (LGPL-2.0-or-later); their original Inkscape metadata, element names, margin hints and licence notices are preserved, and each file carries an added XML comment naming the Breeze original and the modification. `metadata.json` keeps the KDE Visual Design Group as an author and adds the Nightshift adaptation; it does not claim KDE authorship and does not relicense anything. See `README.md` for the full attribution statement.

The outline is drawn with the `ColorScheme-Frame` class, so its colour follows KDE's own frame-contrast rule (a blend of the Window background and text, tuned by `[KDE] frameContrast` in `kdeglobals`). Retuning the palette therefore retunes the edge.

## 8. Mapping to KDE keys

`color-schemes/MT-Nightshift.colors` and `themes/mt-nightshift/colors` carry the same values. The theme copy is what Plasma uses to tint its SVGs; the global copy is what applications and the widget style use. Keep them in sync — they are the only two places the palette is written down.

| Design token | KDE key |
| --- | --- |
| carbon base | `[Colors:Window] BackgroundNormal` |
| content well | `[Colors:View] BackgroundNormal` |
| control | `[Colors:Button] BackgroundNormal` |
| header strip | `[Colors:Header] BackgroundNormal` |
| overlay surface | `[Colors:Tooltip] BackgroundNormal` |
| selection fill | `[Colors:Selection] BackgroundNormal` |
| body text | `ForegroundNormal` in each group |
| secondary text | `ForegroundInactive` |
| accent text | `ForegroundActive` |
| focus ring | `DecorationFocus` |
| hover ring | `DecorationHover` |
| frame line | `ColorScheme-Frame` = mix(background, foreground, `[KDE] frameContrast`) |

`[KDE] contrast=4` is kept from Breeze; it is the shading slot the widget style reads. The frame line does not use it: KDE mixes with `[KDE] frameContrast` instead, which is 0.2 on a stock install and leaves the line at about `#3B3D42` over the carbon base (measured: `blend(Window, ForegroundNormal, 0.2)` = `#3B3D42`). This theme ships `[KDE] frameContrast=0.05` in the Global Theme defaults (0.14 until the 2026-11 polish pass), so *derived* interior seams sit at `#1B1D21` over `Window` and `#202327` over `Header` — 1.11:1 and 1.13:1, whispers rather than borders. The window decoration's own outer line does not take that value: Breeze derives its client hairline from the brighter `Header` background, so at equal contrast the client seam wins. The decoration therefore uses an explicit per-variant `frame_line` token (`decoration.md` §2): Nightshift's `#222529` (1.16:1) was derived as `blend(Header, ForegroundNormal, 0.06)`, keeping the outer edge just dominant without drawing a visible frame, while Nord Day needs one step more (0.07, `#D8DCE4`) to hold the corner arc's light-surface coverage floor. The old `frame_line_contrast` parameter survives only as the recorded derivation in `PARAMS`, not as a runtime colour mix. `[WM]` carries the same family so the Breeze window decoration (if used) matches the header without a separate decoration package.

## 9. Accessibility

- Every `Foreground*` role ≥ **4.66:1** against *both* the `BackgroundNormal` and `BackgroundAlternate` of its own group — 64 checks, 128 measurements, `Header[Inactive]` and the selection fill included. Body text runs 11.9–16.5:1. All five variants are re-measured mechanically by `tools/theme-audit/check-theme.py` in `make check`, so a retuned colour cannot ship below the floor again.
- Non-text UI (outlines, indicators, toggle tracks) ≥ 3:1 against their own surface; selection fill 3.4:1 against `Window`.
- Focus is never conveyed by colour alone: focus draws a ring (Breeze draws a double outline) *and* is the strongest outline accent in the palette, 5.7:1 against the panel and 5.0:1 against a button. On a light surface the same rule reads as the *darkest* outline — Dayshift's focus is `#2A7FA8` against a hover of `#2E8DBE` (`variants.md` §1).
- Inactive windows are not washed out (`[ColorEffects:Inactive]` stays disabled); only the header group gets a deliberately dimmer title (`#C8CED6`, 11:1), which is enough to tell windows apart without making them hard to read.
- No pure black and no pure white: `#0A0B0D` … `#E8EBF0` keeps halation low on OLED and avoids the "floating text" effect of `#000`/`#FFF`.
- State colours are distinguishable in greyscale by lightness: rest (L\* 11.6) → hover outline (L\* 50) → selected fill (L\* 44) → focus outline (L\* 59).

Lowest ratio per group, and the role that sets it:

| Group | Floor | Binding role |
| --- | --- | --- |
| `Button` | 4.67:1 | `ForegroundInactive` on the alternate |
| `Complementary` | 4.67:1 | `ForegroundInactive` on the alternate |
| `Header` | 6.02:1 | `ForegroundInactive` on the normal |
| `Header[Inactive]` | 4.78:1 | `ForegroundInactive` on the alternate |
| `Selection` | 4.66:1 | `ForegroundPositive` on the fill |
| `Tooltip` | 4.81:1 | `ForegroundInactive` on the alternate |
| `View` | 6.65:1 | `ForegroundInactive` on the alternate |
| `Window` | 5.89:1 | `ForegroundInactive` on the alternate |

The binding token is the dim label, not the body text: `ForegroundInactive` is deliberately the closest value to its background, so it is the one to re-check whenever a surface is retuned. The measurement methodology and exact floors are in `validation-tools.md`; the suite's limits are in `validation.md`.

## 10. Maintenance

- Change a colour in `color-schemes/<variant>.colors`, then copy it over `themes/<style>/colors` and `themes/<style>-global/contents/colors` in the same commit, naming the token from §2. The three copies must be byte-identical; `tools/theme-audit/check-theme.py` fails when they differ and re-measures the contrast floors of all five variants.
- Do not add overrides for assets that already respond to `ColorScheme-*`; check the asset for `class="ColorScheme-…"` before copying it.
- Keep the `6px`/`32×32` frame geometry if an asset is re-derived, or panel and dialog margins will drift.
- Re-derive **all three slots at once** (`<path>`, `solid/<path>`, `translucent/<path>`). They are one surface, so they must stay byte-identical; verify with `sha256sum themes/mt-nightshift/{,solid/,translucent/}widgets/tooltip.svgz`, which must print a single hash.
- Never hand-edit a frame corner. `tools/plasma-theme/dialog-frame.py` builds the dialog frame from Breeze's solid slices plus the tooltip's 6px corners, and `tools/plasma-theme/applet-background.py` builds the 14px popup frame; both `--check` runs are in `make check`. Two failures shipped from hand derivation: a band drawn as a chord instead of an annulus (a diagonal seam), and corner artwork smaller than its border, which KSvg then stretches (a distorted arc with a band three times too thick).
- Inside a frame slice, draw the outline as **filled geometry, never as a stroke**. FrameSvg maps each element's bounding box onto its tile, and a stroke inflates that box by half its width: the slice is then mapped slightly smaller and inset, which opens a seam at the corners and, on a wide panel, eats pixels at both ends. Filled shapes keep the bounds exactly as Breeze's.
- Re-validate after any override: JSON parses, `.colors` parses as KDE configuration, package installs with `kpackagetool6`, theme applies in a user-local path, and every runtime request resolves inside the theme — the direct ones (`solid/widgets/tooltip`, `solid/widgets/panel-background`) included.
- Version the style in `metadata.json` (`Version`) whenever an asset **or** a value in `themes/mt-nightshift/colors` changes; Plasma caches themed pixmaps against that value, so a colour edit without a bump can keep serving the old tint.
- Keep `themes/mt-nightshift-global/contents/colors` as a **regular file** containing the byte-identical global `.colors` scheme. Plasma's Look-and-Feel package declares this path as a file; a directory passes loose package validation but applies as an empty config and can erase the complete application palette.

## 11. Out of scope

The Qt Widgets Application Style is implemented separately (`application-style.md`). It is a compiled plugin and is not bundled by the Global Theme; the host requires system plugin installation before it appears in System Settings. The Aurorae decoration in §12 supplies rounded window frames. Cursors, icon theme, splash screen and login theme remain unchanged.

## 12. Window decoration (Aurorae, separate package)

The Aurorae decoration has its own specification: **[`decoration.md`](decoration.md)**.
It covers the geometry, the shadow envelope, the corner band, the generated artwork,
the button set, the title and button row, and the licensing of that package.

The shape tier it belongs to is defined in §6 above: the window corner is 10px,
the same `kControlRadius` every control, hover pill and tooltip uses.


## 13. Application Style (Qt Widgets)

The Qt Widgets application style has its own specification: **[`application-style.md`](application-style.md)**.
It covers the QProxyStyle relationship with Breeze, the field family, the KIO path
bar, item-view focus and selection, tooltips, installation and the restart rule.

Its shape tier is defined in §6 above: a shared 10px maximum radius for controls and
their hover, pressed and focus states.

## 14. Palette variants

Dayshift (the light counterpart) and One Dark Pro (the fifth palette) are documented
in **[`variants.md`](variants.md)**, together with what each needed beyond a straight
retone. Nightshift is the reference palette in §2; the shared design language in
§1–§11 applies to all five.

