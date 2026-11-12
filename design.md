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
| `View` alternate | `#0F1114` | 5.0 | alternating rows, zebra striping |
| `Window` background | `#101216` | 5.4 | panels, dialogs, menus, popups, OSD — the base "carbon" surface |
| `Window` alternate | `#171A1F` | 9.2 | secondary window areas, grouped sections |
| `Header` background | `#15181C` | 8.1 | title areas, toolbars, tab bars, header rows |
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
| Negative | `#EA717C` | 6.4:1 | 4.70:1 (`Button` alternate) | errors, destructive actions |
| Neutral | `#F0A32B` | 8.9:1 | 6.6:1 (`Button` alternate) | warnings, "needs attention" |
| Positive | `#4BC97A` | 8.9:1 | 6.5:1 (`Button` alternate) | success, connected, done |

Normal text is `#E8EBF0` rather than `#FFFFFF`: at these background levels white is a light source on an OLED panel, and the 15:1 ratio is already beyond comfortable.

**How these numbers are measured.** Every `Foreground*` role is checked twice: against the `BackgroundNormal` *and* the `BackgroundAlternate` of the group that owns it, because rows, strips and raised controls do use the alternate. That is eight groups (`Button`, `Complementary`, `Header`, `Header[Inactive]`, `Selection`, `Tooltip`, `View`, `Window`) × eight roles = 64 checks, each measured against two backgrounds, so 128 measurements. Ratios use the WCAG 2.1 relative-luminance formula on sRGB values, with no rounding inside the calculation. The lowest ratio in the palette is **4.66:1** (`Selection` positive on `#1F6E9C`); the lowest outside the selection fill is 4.67:1 (`ForegroundInactive` on the alternate surfaces). `#EA717C` is not a stylistic preference: the previous red, `#E8636F`, measured 4.24:1 on the `Button`/`Complementary` alternate `#12303F` and 4.37:1 on the tooltip alternate `#262B33`, so the shared error colour was lifted just far enough to clear 4.5:1 on the worst of them while keeping its hue and saturation.

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
| Pressed | `Selection` `#1F6E9C` at full strength, or `Selection` at ~33% for toolbar buttons | fill only; geometry never moves |
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

- **Frame radius 6px**, taken from Breeze's frame slices. Panels, dialogs and tooltips keep the `6px` band and `32×32` centre, so the three surfaces this theme owns share one corner language. Applet backgrounds keep Breeze's current variant (14px insets, same 6px radius).
- **Content inset 4px** (`hint-*-margin`) for panels, dialogs and tooltips — Breeze's value. Text sits 4px inside a panel edge; controls add their own padding on top. Applet backgrounds keep their 14px inset, which is what Breeze's current widgets are laid out for.
- **Panels** keep Breeze's 6px margins, so panel thickness and widget spacing are unchanged.
- **Edge treatment:** a 1px `ColorScheme-Frame` line on the outer contour of the frame assets this theme ships, inside the surface. KDE derives that colour as a mix of the `Window` background and text, tuned by `[KDE] frameContrast`, so the edge stays in family if the palette is retuned.
- **Shadow:** Breeze's existing cast shadow is kept, unmodified. It provides separation from the wallpaper; it is not part of the surface.
- **Owned shell surfaces have no gradients, translucency, glow, or inner highlight bevel.** The Breeze "solid" slice set omits Breeze's 50%-alpha inner highlight lines. Inherited button and control artwork retains its original Breeze gradients/shadows for state shading; redrawing those controls is outside this first pass.
- **Blur is switched off** at theme level (`[BlurBehindEffect] enabled=false`), because there is nothing translucent left to blur; a blur behind an already near-black shadow only produces a haze.
- **Adaptive transparency is switched off** (`[AdaptiveTransparency] enabled=false`), because the surfaces are already opaque; adapting them would only add movement.

## 7. Plasma Style asset strategy

Inheritance first, overrides only where the palette cannot reach.

**Inherited from the system Breeze `default` theme** (unchanged, tinted by this theme's `colors`): every widget, control, icon and indicator asset — buttons, line edits, sliders, switches, checkboxes, radiobuttons, scrollbars, tab bars, task manager, pager, clock, calendar, notes, media delegates, margins/highlights, all `icons/*`. These assets reference Breeze `ColorScheme-*` CSS classes, so the Nightshift palette drives them with no file copies.

**Overridden** in `themes/mt-nightshift/` — three surfaces, each shipped at every lookup slot Plasma can ask for. Every copy derives from Breeze's own `solid/` slice set (identical slice names, margins, insets and 6px radius; opaque fills; no translucent inner highlight), with the 1px frame line from §6 added inside the contour.

| Surface | Slots shipped | What asks for it |
| --- | --- | --- |
| panel | `widgets/panel-background`, `solid/widgets/panel-background`, `translucent/widgets/panel-background` | `Panel.qml`: base frame for the adaptive/translucent item, `solid/…` for the opaque and floating-opaque items |
| menu popup, combobox popup, tooltip | `widgets/tooltip`, `solid/widgets/tooltip`, `translucent/widgets/tooltip` | `PlasmaComponents` `Menu.qml` and `ComboBox.qml` (Window colour set) plus `ToolTip.qml` (Tooltip colour set) request `solid/widgets/tooltip` **directly** |
| dialog, popup, OSD | `dialogs/background`, `solid/dialogs/background`, `translucent/dialogs/background` | `LockOsd.qml`, `PlasmoidHeading.qml`, `BackgroundMetrics.qml`, `PlasmaCore.Dialog` |

Three facts fix this layout:

1. **Direct requests bypass the base name.** `Menu.qml`, `ComboBox.qml` and `ToolTip.qml` hard-code `imagePath: "solid/widgets/tooltip"`, and `Panel.qml` hard-codes `solid/widgets/panel-background` for opaque panels. A theme that ships only `widgets/tooltip` resolves those requests to `default/solid/…` — stock Breeze artwork, tinted with our palette, but with no 1px edge and Breeze's own slice treatment. Shipping the `solid/` slot is the only way to keep menus, comboboxes, tooltips and opaque panels on the same surface.
2. **The `translucent/` slot is live on Wayland.** Plasma selects `translucent/` whenever `KWindowEffects::isEffectAvailable(BackgroundContrast)` is true — a KWin-side condition that `[BlurBehindEffect] enabled=false` does not influence. Lookup order is `theme/translucent/<path>` → `theme/<path>` → `default/translucent/<path>` → `default/<path>`, so the base copy would still win, and the translucent copies exist to make the answer explicit and keep it correct if a selector path is ever requested directly, exactly as `solid/` is today.
3. **All three copies are byte-identical.** Breeze's base, `solid/` and `translucent/` slices for these three surfaces share one hint grid, so a single derivation serves every slot: the theme simply has no translucent variant. Identical output is verified with `sha256` (§10).

`opaque/` is deliberately not shipped. Plasma selects it only when compositing is off (X11 without a compositor), which the Wayland target never does, and `theme/opaque/<path>` falls back to `theme/<path>` in any case.

`widgets/background.svgz` (applet and containment backgrounds) is **not** overridden: Breeze's current version already paints at full opacity with its own `ColorScheme-Frame` edge and 14px content insets. Copying the older opaque variant from `solid/` would have cut those insets to 4px and changed widget layout — the inheritance is both lighter and more correct.

Nothing else is copied. If a future Breeze release changes a shared asset, this theme picks it up automatically.

**Derivation and licences.** The three surfaces (nine files: one per selector slot, generated from one derivation) are derived from KDE Breeze (LGPL-2.0-or-later); their original Inkscape metadata, element names, margin hints and licence notices are preserved, and each file carries an added XML comment naming the Breeze original and the modification. `metadata.json` keeps the KDE Visual Design Group as an author and adds the Nightshift adaptation; it does not claim KDE authorship and does not relicense anything. See `README.md` for the full attribution statement.

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

`[KDE] contrast=4` is kept from Breeze; it is the shading slot the widget style reads. The frame line does not use it: KDE mixes with `[KDE] frameContrast` instead, which is 0.2 on a stock install and leaves the line at about `#3B3D42` over the carbon base (measured: `blend(Window, ForegroundNormal, 0.2)` = `#3B3D42`). This theme ships `[KDE] frameContrast=0.14` in the Global Theme defaults, so *derived* interior seams sit at `#33363A`/`#2E3035`. The window decoration's own outer line does not take that value: Breeze derives its client hairline from the brighter `Header` background, so at equal contrast the client seam wins. The decoration therefore mixes at `frame_line_contrast=0.20` from the `Header` group and lands on `#3F4246`, keeping the outer edge the dominant line — see §12.2. `[WM]` carries the same family so the Breeze window decoration (if used) matches the header without a separate decoration package.

## 9. Accessibility

- Every `Foreground*` role ≥ **4.66:1** against *both* the `BackgroundNormal` and `BackgroundAlternate` of its own group — 64 checks, 128 measurements, `Header[Inactive]` and the selection fill included. Body text runs 11.9–16.5:1.
- Non-text UI (outlines, indicators, toggle tracks) ≥ 3:1 against their own surface; selection fill 3.4:1 against `Window`.
- Focus is never conveyed by colour alone: focus draws a ring (Breeze draws a double outline) *and* is the brightest outline accent in the palette, 5.7:1 against the panel and 5.0:1 against a button.
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
| `View` | 6.39:1 | `ForegroundInactive` on the alternate |
| `Window` | 5.89:1 | `ForegroundInactive` on the alternate |

The binding token is the dim label, not the body text: `ForegroundInactive` is deliberately the closest value to its background, so it is the one to re-check whenever a surface is retuned.

## 10. Maintenance

- Change a colour in both `colors` files, in one commit, naming the token from §2.
- Do not add overrides for assets that already respond to `ColorScheme-*`; check the asset for `class="ColorScheme-…"` before copying it.
- Keep the `6px`/`32×32` frame geometry if an asset is re-derived, or panel and dialog margins will drift.
- Re-derive **all three slots at once** (`<path>`, `solid/<path>`, `translucent/<path>`). They are one surface, so they must stay byte-identical; verify with `sha256sum themes/mt-nightshift/{,solid/,translucent/}widgets/tooltip.svgz`, which must print a single hash.
- Inside a frame slice, draw the outline as **filled geometry, never as a stroke**. FrameSvg maps each element's bounding box onto its tile, and a stroke inflates that box by half its width: the slice is then mapped slightly smaller and inset, which opens a seam at the corners and, on a wide panel, eats pixels at both ends. Filled shapes keep the bounds exactly as Breeze's.
- Re-validate after any override: JSON parses, `.colors` parses as KDE configuration, package installs with `kpackagetool6`, theme applies in a user-local path, and every runtime request resolves inside the theme — the direct ones (`solid/widgets/tooltip`, `solid/widgets/panel-background`) included.
- Version the style in `metadata.json` (`Version`) whenever an asset **or** a value in `themes/mt-nightshift/colors` changes; Plasma caches themed pixmaps against that value, so a colour edit without a bump can keep serving the old tint.
- Keep `themes/mt-nightshift-global/contents/colors` as a **regular file** containing the byte-identical global `.colors` scheme. Plasma's Look-and-Feel package declares this path as a file; a directory passes loose package validation but applies as an empty config and can erase the complete application palette.

## 11. Out of scope

The Qt Widgets Application Style is implemented separately in §13. It is a compiled plugin and is not bundled by the Global Theme; the host requires system plugin installation before it appears in System Settings. The Aurorae decoration in §12 supplies rounded window frames. Cursors, icon theme, splash screen and login theme remain unchanged.

## 12. Window decoration (Aurorae, separate package)

`themes/aurorae/MTNightshift/` is the **Sculpted** window edge: a user-local Aurorae decoration for the same palette. It is deliberately separate from the Plasma Style: it does not change the 6px panel/dialog/tooltip radius in §6, and installing one does not install the other. The 15px corner is the **window** corner only.

### 12.1 Geometry

- **15px outer corners**, drawn as a true quarter-circle in the four corner tiles, with a 1px `ColorScheme-Frame` line inside the contour. Fills are opaque; there is no gradient or inner highlight.
- **Title bar 39px at 1x**: 7px above, a 24px title/button row, 8px below. The caption is centred between the button groups and uses KWin's title font; the SVG contains no text or fonts.
- **Buttons 24×24**, 8px apart, 10px from the frame edge. KWin builds both groups from its own settings (`ButtonsOnLeft` defaults to `MSE`, `ButtonsOnRight` to `HIAX`); the theme only supplies the artwork, and a button without an SVG is dropped from the group. Shipped: `minimize`, `maximize`, `restore`, `close`, and `menu` for the window-menu button. The `LeftButtons`/`RightButtons` keys in `MTNightshiftrc` are v1 keys and are not read by Aurorae v2.
- **Shadow ring 32px, ramp across the whole ring**, drawn as four gradient ramps rather than stacked flat-alpha slices: one linear ramp per edge and one radial ramp per corner, all on the same envelope — 0.26 alpha at the contour, 0 at 32px. The original ramp was 0.384 and read as a heavy dark halo on a bright wallpaper; 0.26 over the full ring keeps separation, softens the falloff and leaves no dead ring, since the reserved `padding` is what KWin caches for the life of the compositor (shrinking it shifts every client by the difference until the session restarts). `visible` can be set shorter than `padding` to concentrate the shadow if that trade is ever wanted. The corner ramps are radial about the corner arc centre, so the cast shadow wraps the 15px silhouette instead of stopping at the tangent points; the shadow meets the straight edges continuously and is never painted inside the window rectangle. Because the ramps are radial, no corner cutout mask is needed or shipped. A slice-based shadow (nested flat rects) re-creates visible alpha stairs on its 2–5px bands, which is why the ramps are gradients.
- **The border must run round the corners.** Each corner's frame line is an annulus between the silhouette arc (`r` = 15) and a *concentric* arc at `r` = 14; both must share the corner centre, or the band becomes a lune that thins to ~0.4px at the 45° point and reads as a missing border on a light wallpaper. Two further causes were measured: a 1px annulus only reaches ~50% coverage per pixel where the curve runs diagonally, so the arcs are stroked `frame_line_arc` = 2px (inside the contour, stopped 6° short of each tangent so the cap cannot leak into the shadow ring) while the straight edges stay 1px; and with a 6px border the client's square corner sits at (15 − 6)·√2 = 12.7 from the arc centre, so it must fall inside the band's inner edge or the client paints the corner border away — which is what kept the bottom corners empty. Measured live before: top-left 0.85 mean, the other three 0.35 with 0.00 at the diagonal, and 0.00 under the client; after: all four 0.95 mean / 0.78 minimum.
- **Corner language: 15px, Normal border.** Restoring the earlier 21px corner needs `BorderSize=VeryLarge` (border 8) to clear the client's corner, and that thickens every window frame in the session — a user preference, not a theme property. 15px is the roundest radius that still leaves the border visible at the default border, and `build-decoration.py` refuses any radius/border pair that would bury it again.
- **HiDPI: 2px is a 1x compensation.** Re-rendered at 2x, a 1px arc already reaches 0.94 minimum corner coverage (it is 0.36 at 1x), so the extra pixel exists only to beat 1x antialiasing; on a 2x display the artwork would read as a proportionally heavier corner. Regenerate with `--arc 1.0` there — `make check-dpr2` verifies exactly that configuration.
- **Where the radial stops.** Each top corner element also spans 18px of straight window edge below the arc, and a radial ramp under-darkens that strip, so the top corner elements carry a linear `shadow-left`/`shadow-right` strip there and the radial rect is clipped to the 45×45 corner square — the two must not overlap, or the alpha composites (two 0.26 layers composite to 0.45 and the tangent point turns into a dark blob). The bottom corner elements need no strip: their arc is tangent to the window's left edge at the element's own top row, so the whole element is corner territory. Adding one there painted a darker band into the bottom corners and stepped the shadow where the side element ends.
- **Checks:** `tools/decoration-probe/check-decoration.py` rasterises every slice through Qt's qsvg plugin, re-stitches the frame and asserts the invariants that have broken before (ramped edges, shadow in the corner cutouts, no alpha above the envelope, no divider row, expected fills). Run it after any change to this file.
- **No title divider.** Breeze paints the toolbar area of a Qt Widgets window with the `Header` palette group and closes it with a 1px frame line derived from `[KDE] frameContrast` — measured as `blend(Header, ForegroundNormal, frameContrast)` = `#33363A` at the theme's 0.14. That line sits 7px below the 39px boundary, so a divider in the SVG put a second, darker seam (`#0A0B0D`) 8px above the real edge and split one continuous header-toned surface in two. The SVG therefore ends the header flush at 39px and leaves the single separator to the client. Windows whose client area is not header-toned still separate by the `Header` `#15181C` → `Window` `#101216` tone step, which is how Breeze itself separates them.
- **Maximized**: a 32px flat header (4px + 24px + 4px), no corners, no shadow.

### 12.2 Palette

| Element | Colour |
| --- | --- |
| Active header | `#15181C` (`Header` background) |
| Inactive header | `#101216` (`Header[Inactive]` background) |
| Frame sides and bottom | `#101216` (`Window` background) |
| Frame line | `#3F4246` = `blend(Header, ForegroundNormal, 0.20)`, deliberately stronger than the derived interior seams so the outer edge stays dominant (§8) |
| Active title | `#E8EBF0` |
| Inactive title | `#C8CED6` |
| Active button icon | `#C8CED6` |
| Hover icon / pressed icon | `#E8EBF0` / `#FFFFFF` active; `#C8CED6` / `#FFFFFF` inactive |
| Inactive button icon | `#8D97A4` |
| Disabled button icon | `#5F6874` active, `#4A525C` inactive |
| Hover outline | `#2A7FA8` active, `#3B3D42` inactive |
| Pressed fill | `#1F6E9C` active, `#174E70` inactive |
| Close hover / pressed (active) | `#EA717C` (`ForegroundNegative`); the pressed glyph is `#101216` |

### 12.3 States

- **Rest**: no button background, icon only.
- **Hover**: 1px outline with a 6px rounded-square radius, no fill; the icon brightens.
- **Pressed**: a filled 6px rounded-square disc with a white glyph and no outline.
- **Disabled**: a dimmed glyph, no disc.
- **Inactive window**: buttons drop to the inactive icon colour; hover-inactive uses the neutral outline; pressed-inactive uses `#174E70`.
- State changes never move or resize a control. The close button is the only place the negative colour is used, and only on hover/press.

### 12.4 HiDPI and Aurorae constraints

- Geometry is vector. KWin renders the SVG at the window's device pixel ratio, so the 1px frame line and 1.5–1.6px glyph strokes stay at 1 and 1.5–1.6 logical pixels at 2x.
- Aurorae clamps `BorderLeft`/`BorderRight`/`BorderBottom` to KWin's **BorderSize** setting. At the default Normal size the frame is `6/6/6`; the 15px arc then stays clear of the client's square corner. Tiny/NoSides (1–4px) can show a small notch at the bottom corners because the client is inset less than the arc; the shadow still carries the silhouette. `None` hides the bottom arc entirely.
- Aurorae v2 derives the window shadow from the decoration's padding ring and cuts it at the window rectangle. The `mask-*` elements are supplied for the blur region; v2 uses them for blur only, and blur is disabled in this theme.
- **Three knobs tune the shell**, all in `PARAMS`: `peak` (cast-shadow weight), `frame_line_contrast` (how far the outer line sits above the fill) and `frame_line_arc` (arc thickness). `build-decoration.py` takes `--padding/--visible/--peak/--arc` overrides for a one-off trial, and `make check` / `make apply` wrap the verify and install sequences.
- **Corner tiles must be named `topleft`, `topright`, `bottomleft`, `bottomright`.** `FrameSvg` resolves the corners through `FrameSvgHelpers::borderToElementId()`, so a tile named `tl`/`br` is never requested: the corner stays transparent, the header and side fills lose their ends, and the shadow splits into four detached bars. FrameSvg also scales each corner element to its section rect, which is `leftMargin × topMargin` for the top corners and `leftMargin × bottomMargin` for the bottom ones; keep the element sizes at `45×63` and `45×45` (padding + radius, or padding + header for the top corners) — `tools/decoration-probe/build-decoration.py` derives them from one padding value. Check a change with a real `FrameSvg` render, not a plain SVG preview.
- **The window-menu button needs `menu.svg`.** `ButtonsOnLeft` defaults to `MSE`, and v2 instantiates the menu button even when the theme has no artwork: without `menu.svg` it falls back to `FallbackMenuDecorationButton`, which paints the full-colour window icon (a blue Dolphin icon on a dark titlebar). `menu.svg` carries the same eight state prefixes as the other buttons and the same three-rule glyph in `#C8CED6`.
- **Button paths are resolved once per KWin process.** `DecorationTheme` keeps every resolved path in a `Q_GLOBAL_STATIC` list and `onDecorationSettingsChanged()` only reparses `auroraerc`; adding or renaming a button SVG therefore has no effect until KWin restarts — `reconfigure`, a new window, or switching the theme away and back all reuse the cached object, so a fresh window shows new `decoration.svg` pixels but keeps the old button paths. Validate a new button file only after a KWin restart. The v1 QML engine (`org.kde.kwin.aurorae`) has no `menu.svg` lookup at all: its `MenuButton.qml` always paints the window icon, so the themed glyph appears only under `org.kde.kwin.aurorae.v2`.
- `decoration-maximized` and `decoration-maximized-inactive` are top strips; KWin clips decoration painting to the title border. Maximize and restore use separate `maximize.svg` and `restore.svg` files, each carrying all eight button-state prefixes.
- The title/button row is tuned for the default title font and `ButtonSize` (100%). KWin grows the titlebar when the button-size factor grows, but the SVG header slice is fixed at 39px; the extra height is painted with the `Window` centre colour and the header boundary stays at 39px. Keep the default size for the intended single-tone header.
- Shadow is not drawn when the window is maximized; Aurorae v2 sets a null shadow and the maximized header is flat.
- `metadata.desktop` (with `Type=Service`, `Name` and `X-KDE-PluginInfo-Name=MTNightshift`) is the package entry. Aurorae themes are plain directory themes, not KPackage bundles, so `kpackagetool6` does not apply.

The Aurorae artwork is original and licensed LGPL-2.0-or-later. No upstream Breeze file is copied or modified by this package. The derived Plasma Style omits a blanket package license because its upstream assets carry multiple file-level licenses; preserve each file's original notices.

## 13. Application Style (Qt Widgets)

`application-style/` provides the `MTNightshift` QStyle key. It is an original `QProxyStyle` over the installed Breeze QStyle: buttons, line edits, non-editable combo boxes, checkboxes and radio indicators receive the Sculpted control treatment; labels, icons, geometry and other controls remain delegated to Breeze. The design uses a 15px maximum corner radius, clamped for small controls, and reads colors from the active Qt palette so the MT Nightshift scheme supplies its dark surfaces and blue states. Framed line edits and non-editable combo boxes use borderless filled surfaces with focus-only accent rings; frameless edits and the editable-combo/spin-box child editors stay with Breeze. KIO path bars are handled separately: `KUrlNavigator` (and Dolphin's subclass) paints itself through `PE_FrameLineEdit`, not `PE_PanelLineEdit`, so the style intercepts that primitive for any widget whose meta-object chain contains the public class name `KUrlNavigator` and fills the same borderless rounded surface from the widget's `Base` tone. That covers Dolphin and other KIO file dialogs without app-name coupling; ordinary widgets drawing `PE_FrameLineEdit` keep Breeze's frame. The navigator sets `State_HasFocus` only while editing or with its context menu open, so the accent ring appears in those states only. The Dolphin Places dock separator is suppressed only in Dolphin's main window, while the dock remains resizable. The thin horizontal toolbar/window-background hairline remains because Qt/Breeze paints it in a broader background pass; removing only that row would require a fragile buffered repaint.

The plugin affects Qt Widgets applications; Qt Quick/Kirigami apps and Plasma's own controls use separate styling systems. The `.themerc` file provides the System Settings display name; the plugin and metadata are installed in `/usr/lib64/qt6/plugins/styles/` and `/usr/share/kstyle/themes/`. The Global Theme selects `MTNightshift` as `widgetStyle`. Rebuild after Qt ABI updates.

The path bar reads as a filled Sculpted field, not a Breeze frame: KIO tints a URL navigator's own `Base` to the toolbar shade, so the style takes the input tone from the application palette instead. Without that the fill matched the toolbar exactly and only the corner antialiasing hinted at the field, which looked like a broken corner radius rather than a rounded field. App tooltips are styled too (`PE_PanelTipLabel`, 6px radius from §6, `ToolTipBase` fill, 1px frame): Breeze's default is a square-cornered frame, which showed up as a stray bordered box wherever a tooltip appeared over the view.

Scrollbars keep Breeze painting and interaction behavior. `PM_ScrollBarExtent` caps their gutter at 12 logical pixels, preserving Breeze's 8px handle. In Dolphin only, the scrollbar owned by the public KIO `KFilePlacesView` in the main window gets a 0px extent, removing its gutter; dialog-hosted Places views retain the slim scrollbar. Detection uses the application name and Qt meta-object class name without linking Dolphin/KIO internals. Overflow in that panel has no visible scrollbar cue, but wheel, keyboard and touch scrolling remain available. The updated plugin is installed; offscreen Qt tests confirm 0px for the Dolphin Places view, 12px for other views and Dolphin dialogs, and wheel scrolling with a long list while the bar has zero width. A fresh Dolphin screenshot confirms the sidebar has no scrollbar; live keyboard/touch testing in Dolphin remains outstanding.

KDE's Qt platform theme prefers the complete `[Colors:*]` groups in `kdeglobals` over the `General/ColorScheme` fallback. An accent-color update can leave partial groups that omit `BackgroundNormal`; KColorScheme then supplies Breeze Light's white default even though `ColorScheme=MT-Nightshift`. If a fresh Qt app reports `QPalette::Base=#ffffff`, switch to another scheme and reapply MT Nightshift so Plasma rewrites the complete palette groups. Verify `Colors:View/BackgroundNormal=10,11,13` and `Colors:Window/BackgroundNormal=16,18,22`.
