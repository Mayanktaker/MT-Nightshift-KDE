#!/usr/bin/env python3
# © Mayanktaker Computers & Web Development | https://mayanktaker.com

"""Build distribution packages for KDE Store and user releases."""

import argparse
import os
import shutil
import sys
import tarfile

VERSION = "1.6.0"

VARIANTS = {
    "nightshift": {
        "name": "MT-Nightshift",
        "style": "mt-nightshift",
        "scheme": "MT-Nightshift",
        "decoration": "MTNightshift",
        "laf": "com.mayanktaker.mt-nightshift.desktop",
        "global_pkg": "mt-nightshift-global",
    },
    "dayshift": {
        "name": "MT-Dayshift",
        "style": "mt-dayshift",
        "scheme": "MT-Dayshift",
        "decoration": "MTDayshift",
        "laf": "com.mayanktaker.mt-dayshift.desktop",
        "global_pkg": "mt-dayshift-global",
    },
    "nord-night": {
        "name": "MT-Nord-Night",
        "style": "mt-nord-night",
        "scheme": "MT-Nord-Night",
        "decoration": "MTNordNight",
        "laf": "com.mayanktaker.mt-nord-night.desktop",
        "global_pkg": "mt-nord-night-global",
    },
    "nord-day": {
        "name": "MT-Nord-Day",
        "style": "mt-nord-day",
        "scheme": "MT-Nord-Day",
        "decoration": "MTNordDay",
        "laf": "com.mayanktaker.mt-nord-day.desktop",
        "global_pkg": "mt-nord-day-global",
    },
    "one-dark-pro": {
        "name": "MT-One-Dark-Pro",
        "style": "mt-one-dark-pro",
        "scheme": "MT-One-Dark-Pro",
        "decoration": "MTOneDarkPro",
        "laf": "com.mayanktaker.mt-one-dark-pro.desktop",
        "global_pkg": "mt-one-dark-pro-global",
    },
}

INSTALLER_TEMPLATE = """#!/bin/bash
# © Mayanktaker Computers & Web Development | https://mayanktaker.com
set -e

# Target paths for user-local KDE Plasma installation.
COLOR_DIR="${{HOME}}/.local/share/color-schemes"
THEME_DIR="${{HOME}}/.local/share/plasma/desktoptheme/{style}"
AURORAE_DIR="${{HOME}}/.local/share/aurorae/themes/{decoration}"

mkdir -p "${{COLOR_DIR}}" "${{THEME_DIR}}" "${{AURORAE_DIR}}"

echo "Installing {name} color scheme..."
install -m 644 color-scheme/{scheme}.colors "${{COLOR_DIR}}/"

echo "Installing {name} Plasma desktop theme..."
cp -r plasma-theme/* "${{THEME_DIR}}/"

echo "Installing {name} Aurorae window decoration..."
cp -r aurorae/* "${{AURORAE_DIR}}/"

echo "Installing {name} Look-and-Feel package..."
kpackagetool6 --type Plasma/LookAndFeel -i look-and-feel || \\
kpackagetool6 --type Plasma/LookAndFeel -u look-and-feel

echo "{name} installed successfully."
echo "To apply, run: plasma-apply-lookandfeel -a {laf}"
"""


def make_tar_gz(source_dir: str, archive_path: str, arcname: str | None = None) -> None:
    """Create a gzip tarball from a source directory."""
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(source_dir, arcname=arcname or os.path.basename(source_dir))


def build_variant_package(variant_key: str, repo_root: str, dist_dir: str) -> str:
    """Build a complete standalone release tarball for a single variant."""
    cfg = VARIANTS[variant_key]
    pkg_name = f"{cfg['name']}-v{VERSION}"
    stage_dir = os.path.join(dist_dir, pkg_name)

    # Recreate clean staging directory.
    if os.path.exists(stage_dir):
        shutil.rmtree(stage_dir)
    os.makedirs(stage_dir, exist_ok=True)

    # 1. Color scheme
    cs_dir = os.path.join(stage_dir, "color-scheme")
    os.makedirs(cs_dir, exist_ok=True)
    shutil.copy2(
        os.path.join(repo_root, "color-schemes", f"{cfg['scheme']}.colors"),
        os.path.join(cs_dir, f"{cfg['scheme']}.colors"),
    )

    # 2. Plasma Desktop Theme
    pt_dir = os.path.join(stage_dir, "plasma-theme")
    shutil.copytree(os.path.join(repo_root, "themes", cfg["style"]), pt_dir)

    # 3. Aurorae Window Decoration
    aur_dir = os.path.join(stage_dir, "aurorae")
    shutil.copytree(os.path.join(repo_root, "themes", "aurorae", cfg["decoration"]), aur_dir)

    # 4. Look-and-Feel package
    laf_dir = os.path.join(stage_dir, "look-and-feel")
    shutil.copytree(os.path.join(repo_root, "themes", cfg["global_pkg"]), laf_dir)

    # 5. Wallpapers
    wp_dir = os.path.join(stage_dir, "wallpapers")
    os.makedirs(wp_dir, exist_ok=True)
    for res in ("1920x1080", "3840x1080"):
        wp_src = os.path.join(repo_root, "Wallpapers", f"{variant_key}-abstract-{res}.png")
        if os.path.exists(wp_src):
            shutil.copy2(wp_src, wp_dir)

    # 6. User installer script
    installer_content = INSTALLER_TEMPLATE.format(
        name=cfg["name"],
        style=cfg["style"],
        scheme=cfg["scheme"],
        decoration=cfg["decoration"],
        laf=cfg["laf"],
    )
    installer_path = os.path.join(stage_dir, "install.sh")
    with open(installer_path, "w", encoding="utf-8") as f:
        f.write(installer_content)
    os.chmod(installer_path, 0o755)

    # 7. Create tarball
    archive_path = os.path.join(dist_dir, f"{pkg_name}.tar.gz")
    make_tar_gz(stage_dir, archive_path, arcname=pkg_name)
    shutil.rmtree(stage_dir)
    print(f"  built {os.path.basename(archive_path)}")

    # 8. Also create KDE Store individual packages
    laf_archive = os.path.join(dist_dir, f"{cfg['laf']}-{VERSION}.tar.gz")
    make_tar_gz(os.path.join(repo_root, "themes", cfg["global_pkg"]), laf_archive, arcname=cfg["laf"])

    aurorae_archive = os.path.join(dist_dir, f"aurorae-{cfg['decoration']}-{VERSION}.tar.gz")
    make_tar_gz(
        os.path.join(repo_root, "themes", "aurorae", cfg["decoration"]),
        aurorae_archive,
        arcname=cfg["decoration"],
    )

    return archive_path


def build_all_packages(repo_root: str) -> None:
    """Build distribution archives for all 5 variants."""
    dist_dir = os.path.join(repo_root, "dist")
    os.makedirs(dist_dir, exist_ok=True)
    print(f"building KDE Store and user release archives in {dist_dir}...")
    for variant in VARIANTS:
        build_variant_package(variant, repo_root, dist_dir)
    print("all packages built successfully.")


def verify_packages(repo_root: str) -> bool:
    """Verify presence and validity of all generated archives."""
    dist_dir = os.path.join(repo_root, "dist")
    if not os.path.exists(dist_dir):
        print("FAIL: dist directory does not exist (run make package)")
        return False

    all_ok = True
    for var, cfg in VARIANTS.items():
        main_tar = os.path.join(dist_dir, f"{cfg['name']}-v{VERSION}.tar.gz")
        laf_tar = os.path.join(dist_dir, f"{cfg['laf']}-{VERSION}.tar.gz")
        aur_tar = os.path.join(dist_dir, f"aurorae-{cfg['decoration']}-{VERSION}.tar.gz")

        for arc in (main_tar, laf_tar, aur_tar):
            if not os.path.exists(arc):
                print(f"  FAIL: missing {os.path.basename(arc)}")
                all_ok = False
            else:
                try:
                    with tarfile.open(arc, "r:gz") as tar:
                        names = tar.getnames()
                        if not names:
                            print(f"  FAIL: empty archive {os.path.basename(arc)}")
                            all_ok = False
                        else:
                            print(f"  OK   {os.path.basename(arc)} ({len(names)} items)")
                except Exception as exc:
                    print(f"  FAIL: corrupted archive {os.path.basename(arc)}: {exc}")
                    all_ok = False

    return all_ok


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify built packages")
    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    if args.check:
        print("verifying distribution packages...")
        ok = verify_packages(repo_root)
        if not ok:
            sys.exit(1)
        print("all distribution packages verified.")
        return

    build_all_packages(repo_root)


if __name__ == "__main__":
    main()
