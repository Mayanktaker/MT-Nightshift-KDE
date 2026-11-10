© Mayanktaker Computers & Web Development | https://mayanktaker.com

# Project map

- **Product:** MT Nightshift KDE theme set: Plasma Style, global color scheme, Plasma Look-and-Feel, Aurorae window decoration, and a Qt Widgets Application Style layered over Breeze.
- **Target environment:** Fedora Linux 45, KDE Plasma 6.8.2. The baseline was copied from `plasma-breeze-common` and `libplasma` 6.8.2-1.fc45.
- **Project type:** KDE theme assets plus a C++17 Qt Widgets plugin; CMake 4.3.0, ECM 6.31.0, Qt 6.11.2, DNF. No standalone application runtime.
- **Deliverables:** `themes/mt-nightshift/` (Plasma Style, ID `mt-nightshift`), `color-schemes/MT-Nightshift.colors`, `themes/mt-nightshift-global/` (Look-and-Feel ID `com.mayanktaker.mt-nightshift.desktop`), `themes/aurorae/MTNightshift/`, and `application-style/` (Qt style key `MTNightshift`).
- **Visual source of truth:** `design.md`. Scope and task state: `PLAN.md`. Provenance and licensing: `README.md`.

## Working rules

- Keep `upstream/` unmodified. Put the new Plasma Style and global color scheme in separate project paths, with a unique MT Dark name and metadata.
- Follow `design.md` for palette, contrast, shape, and interaction-state decisions. Override only the Plasma assets needed; rely on Breeze fallback assets for unchanged elements.
- Preserve KDE contributor credits, embedded copyright/license notices, and per-file licensing. Do not imply KDE endorsement or relicense upstream assets.
- Test data packages through user-local KDE paths (`~/.local/share/plasma/desktoptheme/`, `~/.local/share/plasma/look-and-feel/`, `~/.local/share/color-schemes/`, `~/.local/share/aurorae/themes/`). The Qt style plugin has no user-local Qt search path on this host; system installation requires explicit approval. Record and restore active settings when live-testing.
- Validate metadata as JSON/Desktop Entry, SVG assets as XML, KPackages with `kpackagetool6`, and the Qt plugin with CMake plus an offscreen QStyleFactory smoke test. See `PLAN.md` for the verification sequence.
