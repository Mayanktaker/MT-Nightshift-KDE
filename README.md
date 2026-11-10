© Mayanktaker Computers & Web Development | https://mayanktaker.com

# MT Dark KDE

A personal, darker and more solid evolution of KDE Breeze Dark. The selected direction is **Nightshift OLED**: near-black carbon surfaces, restrained Breeze-blue highlights, and clear, solid layers rather than blur or glass effects.

## Upstream baseline

`upstream/` preserves the official theme assets installed on this Fedora KDE system; customization belongs in separate project files, not in this baseline.

- `upstream/color-schemes/BreezeDark.colors` — global KDE color scheme from `plasma-breeze-common` 6.8.2-1.fc45.
- `upstream/plasma/desktoptheme/breeze-dark/` — Breeze Dark Plasma Style metadata and palette from `plasma-breeze-common` 6.8.2-1.fc45.
- `upstream/plasma/desktoptheme/default/` — shared Breeze Plasma Style assets from `libplasma` 6.8.2-1.fc45; Breeze Dark inherits these assets.

The upstream projects are [KDE Breeze](https://invent.kde.org/plasma/breeze) and [KDE libplasma](https://invent.kde.org/plasma/libplasma). Plasma Style files are under `src/desktoptheme/`; the global palette is `colors/BreezeDark.colors` in KDE Breeze. Package-provided assets are from the host's official Fedora KDE packages, so the baseline matches Plasma 6.8.2.

## Attribution and licensing

The upstream Breeze Dark metadata identifies the KDE Visual Design Group and labels that package LGPL, but the Fedora RPMs include files under multiple licenses. Preserve each source file's notices and check its upstream license before redistributing modified assets; the derived Plasma Style therefore does not claim one blanket license in its metadata. Original code and artwork marked `LGPL-2.0-or-later` are covered by the full license text in [`LICENSES/LGPL-2.0.txt`](LICENSES/LGPL-2.0.txt). The `upstream/` files retain their own terms and notices; see [`LICENSES/README.md`](LICENSES/README.md). This project does not claim KDE authorship or relicense upstream files.

## Theme files

- `themes/mt-nightshift/` — installable Plasma Style (`mt-nightshift`). It overrides only the assets needed for the solid Nightshift surfaces; unmodified assets fall back to system Breeze `default/`.
- `color-schemes/MT-Nightshift.colors` — global application color scheme. Its palette is mirrored in `themes/mt-nightshift/colors`; keep those files synchronized as described in `design.md`.
- `themes/mt-nightshift-global/` — Plasma 6 Global Theme (Look-and-Feel package). It selects the Plasma Style, color scheme, and Aurorae decoration without resetting the desktop layout, icons, cursor, wallpaper, or splash.
- `themes/aurorae/MTNightshift/` — user-local Aurorae window decoration with 21px window corners. The Global Theme manifest references this separate package; it does not contain it.
- `application-style/` — C++ Qt Widgets style plugin (`MTNightshift`) that keeps Breeze behavior while drawing Sculpted controls with approximately 15px corner radii.

The Application Style also removes the Dolphin Places sidebar divider and gives framed path/search inputs borderless, rounded fills with a focus-only ring. A subtle horizontal toolbar hairline remains; removing it would require replacing a larger Breeze window-background paint pass.

The Qt style is installed at `/usr/lib64/qt6/plugins/styles/mtnightshiftstyle.so` with its KStyle metadata at `/usr/share/kstyle/themes/mtnightshift.themerc`, and is selected as the active Qt Widgets style. The Global Theme also selects `MTNightshift`. Qt Quick/Kirigami apps and Plasma controls use separate style systems.

The installed style narrows Qt Widgets scrollbar gutters to 12px and removes the gutter from Dolphin's Places sidebar only; other Dolphin scroll areas and file dialogs keep a slim scrollbar. A fresh Dolphin screenshot confirms the sidebar has no visible scrollbar. Offscreen tests confirm wheel scrolling still works with a long list and the dialog retains a 12px gutter; keyboard/touch interaction in a live Dolphin window remains to be checked.

### Build the Qt style

For this Fedora/Qt installation, configure with the Qt system plugin paths; otherwise ECM may choose `/usr/local/lib64/plugins`, which Qt does not scan:

```bash
cmake -S application-style -B build -DCMAKE_INSTALL_PREFIX=/usr -DKDE_INSTALL_USE_QT_SYS_PATHS=ON
cmake --build build
```

The plugin installs to `$(qtpaths6 --query QT_INSTALL_PLUGINS)/styles/` and its `.themerc` to `/usr/share/kstyle/themes/`. Reinstalling or replacing these system files requires explicit approval.

## User-local testing

Install only into the current user's KDE data directories; do not copy theme files into `/usr/share`:

```bash
install -d ~/.local/share/plasma/desktoptheme ~/.local/share/color-schemes
cp -a themes/mt-nightshift ~/.local/share/plasma/desktoptheme/mt-nightshift
cp color-schemes/MT-Nightshift.colors ~/.local/share/color-schemes/
plasma-apply-desktoptheme mt-nightshift
plasma-apply-colorscheme MT-Nightshift
install -d ~/.local/share/aurorae/themes
cp -a themes/aurorae/MTNightshift ~/.local/share/aurorae/themes/MTNightshift
kpackagetool6 --type Plasma/LookAndFeel --install themes/mt-nightshift-global
plasma-apply-lookandfeel --apply com.mayanktaker.mt-nightshift.desktop
```

Before applying, record the current Look-and-Feel, Plasma Style, color scheme, icons and window decoration; restore those exact selections after visual testing. The Global Theme deliberately omits layout, icons, cursor, wallpaper and splash defaults. The detailed asset strategy and palette are in [`design.md`](design.md).

To remove the local packages, restore your previous selections first. Then run `kpackagetool6 --type Plasma/LookAndFeel --remove com.mayanktaker.mt-nightshift.desktop` and `kpackagetool6 --type Plasma/Theme --remove mt-nightshift`. Move `~/.local/share/aurorae/themes/MTNightshift/` and `~/.local/share/color-schemes/MT-Nightshift.colors` to a backup location to unregister them while keeping recoverable copies.

## Current state

The official baseline in `upstream/` is copied and has not been modified. The Global Theme, MT Nightshift color scheme, Aurorae decoration and Qt Application Style are active; the `QStyleFactory` smoke test reports `MTNightshift` and the active palette base is `#0A0B0D`. Aurorae's corner slices are fixed, but the running KWin process cached the missing menu path, so a full Plasma logout/login is still required to verify the menu glyph. See [`PLAN.md`](PLAN.md).
