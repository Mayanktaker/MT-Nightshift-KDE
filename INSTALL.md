# Installing MT Dark KDE

© Mayanktaker Computers & Web Development | https://mayanktaker.com

Part of the [MT Dark KDE](README.md) suite. Everything here is user-local except the
Qt Widgets style plugin, which must go into the system Qt plugin path.

## Quick start

### Prerequisites

For building the Qt Widgets style plugin and running verification checks, ensure the required toolchain and libraries are installed:

- **Fedora**:
  ```bash
  sudo dnf install -y cmake extra-cmake-modules gcc-c++ qt6-qtbase-devel libxml2 python3-pillow python3-numpy
  ```
- **Arch Linux**:
  ```bash
  sudo pacman -S --needed cmake extra-cmake-modules gcc qt6-base libxml2 python-pillow python-numpy
  ```
- **Ubuntu / Debian** (24.04+):
  ```bash
  sudo apt-get install -y cmake extra-cmake-modules g++ qt6-base-dev libxml2-utils python3-pillow python3-numpy
  ```

---

### Quick Installation (Automated via Make)

The repository provides automated recipes in the `Makefile` to install all data packages user-locally and apply any variant to your running Plasma session:

```bash
# Clone the repository
git clone https://github.com/Mayanktaker/MT-Nightshift-KDE.git
cd MT-Nightshift-KDE

# Install and apply the default MT Nightshift look
make apply

# Or switch directly to any variant
make apply-dayshift       # Applies MT Dayshift
make apply-nord-night     # Applies MT Nord Night
make apply-nord-day       # Applies MT Nord Day
make apply-one-dark-pro   # Applies MT One Dark Pro
```

#### Installing the C++ Qt Widgets Style Plugin (Optional but Recommended)

The Qt plugin is built locally and installed into the path reported by `qtpaths6 --query QT_INSTALL_PLUGINS`. Installing the plugin and its KStyle metadata requires root permissions:

```bash
# Build and install the Qt Widgets style plugin
make style-install
```

`make style-install` validates the detected Qt plugin directory and compares the installed `.so` with the canonical repository build. After installing, start any Qt Widgets application (e.g. Dolphin) or select `MTNightshift` under **System Settings → Appearance → Application Style**. Release tarballs contain the theme assets only; do not copy a plugin binary from another Qt build or distribution because Qt plugin ABI compatibility must match the host.

To revert cleanly:

```bash
make uninstall        # removes the five user-local theme packages
make style-uninstall  # removes the system-wide Qt plugin and its metadata (sudo)
```

---

### Manual / User-Local Installation

If you prefer installing components manually without the `Makefile`:

1. **Aurorae Window Decorations**:
   ```bash
   install -d ~/.local/share/aurorae/themes/
   cp -r themes/aurorae/* ~/.local/share/aurorae/themes/
   ```

2. **Global Color Schemes**:
   ```bash
   install -d ~/.local/share/color-schemes/
   cp color-schemes/*.colors ~/.local/share/color-schemes/
   ```

3. **Plasma Desktop Themes**:
   ```bash
   install -d ~/.local/share/plasma/desktoptheme/
   for style in mt-nightshift mt-dayshift mt-nord-night mt-nord-day mt-one-dark-pro; do
       cp -r themes/$style ~/.local/share/plasma/desktoptheme/
   done
   ```

4. **Global Theme (Look-and-Feel Packages)**:
   ```bash
   for pkg in mt-nightshift-global mt-dayshift-global mt-nord-night-global mt-nord-day-global mt-one-dark-pro-global; do
       kpackagetool6 --type Plasma/LookAndFeel -i themes/$pkg || \
       kpackagetool6 --type Plasma/LookAndFeel -u themes/$pkg
   done
   ```

5. **Activate via Command Line**:
   ```bash
   # Select the Global Look-and-Feel package
   plasma-apply-lookandfeel -a com.mayanktaker.mt-nightshift.desktop

   # Set optimal frame contrast and reconfigure KWin
   kwriteconfig6 --file kdeglobals --group KDE --key frameContrast 0.05
   gdbus call --session --dest org.kde.KWin --object-path /KWin --method org.kde.KWin.reconfigure
   ```

---

### Distributable Packages (KDE Store & Standalone Releases)

Build distributable `.tar.gz` archives for all five variants in `dist/`:

```bash
make package
```

This creates:
- **Complete Suite Tarballs**: `dist/MT-<Variant>-v1.7.0.tar.gz` (contains Look-and-Feel, desktop theme, Aurorae decoration, color scheme, all four matching wallpapers, and a standalone `install.sh` script). The Qt plugin is intentionally excluded and must be built or installed with `make style-install` on the target Qt 6 environment.
- **KDE Store Look-and-Feel Packages**: `dist/com.mayanktaker.<style>.desktop-1.7.0.tar.gz`.
- **KDE Store Aurorae Decoration Packages**: `dist/aurorae-<decoration>-1.7.0.tar.gz`.
- **`SHA256SUMS`**: the checksum manifest for every archive above.

Archive names come from the version in the shipped `metadata.json` / `metadata.desktop`
files, not from a literal in the packaging script, so a release cannot be cut whose
archive names disagree with the metadata inside them.

#### Cutting a release

```bash
make release-check      # check + package, then prints the exact tag commands
```

Run it immediately before tagging. The release workflow (`.github/workflows/release.yml`)
only discovers a version mismatch **after** the tag is public, so `release-check` is the
gate that catches it locally:

```bash
git tag -a v<version> -m "MT Dark KDE <version>"
git push && git push origin v<version>
```

The tag builds the archives, verifies them, and attaches them with `SHA256SUMS` to the
GitHub Release.

---
