#!/usr/bin/env python3
# © Mayanktaker Computers & Web Development | https://mayanktaker.com

"""Build and verify minimal abstract wallpapers for all MT theme variants."""

import argparse
import os
import sys
from PIL import Image

# Canonical list of theme variants and their palette definitions.
VARIANTS = {
    "nightshift": {
        "title": "MT Nightshift (dark)",
        "dominant": "#101216",
        "deep": "#0A0B0D",
        "mid": "#1B1F25",
        "accent": "#1F6E9C",
        "highlight": "#4FB4E6",
        "prefix": "nightshift",
    },
    "dayshift": {
        "title": "MT Dayshift (light)",
        "dominant": "#EFF1F5",
        "lightest": "#FAFBFD",
        "mid": "#F4F6F9",
        "accent": "#1F6E9C",
        "highlight": "#256D9F",
        "prefix": "dayshift",
    },
    "nord-night": {
        "title": "MT Nord Night (dark)",
        "dominant": "#2E3440",
        "deep": "#232932",
        "mid": "#3B4252",
        "accent": "#84A5C6",
        "highlight": "#A9CEE0",
        "prefix": "nord-night",
    },
    "nord-day": {
        "title": "MT Nord Day (light)",
        "dominant": "#ECEFF4",
        "lightest": "#F7F9FC",
        "mid": "#E5E9F0",
        "accent": "#4C6B91",
        "highlight": "#1F5F8C",
        "prefix": "nord-day",
    },
    "one-dark-pro": {
        "title": "MT One Dark Pro (dark)",
        "dominant": "#282C34",
        "deep": "#1D1F23",
        "mid": "#404754",
        "accent": "#528BFF",
        "highlight": "#7FBEF2",
        "prefix": "one-dark-pro",
    },
}

# Resolutions generated for each variant.
TARGET_RESOLUTIONS = [
    ("1920x1080", 1920, 1080, "16:9 Full HD"),
    ("3840x1080", 3840, 1080, "32:9 Panoramic Dual-FHD"),
    ("5120x1440", 5120, 1440, "32:9 Panoramic Dual-QHD"),
    ("3840x2160", 3840, 2160, "16:9 4K UHD"),
]


def render_16x9(src_img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Scale and crop a 16:9 composition to exact target dimensions."""
    src_w, src_h = src_img.size
    scale = target_h / src_h
    scaled_w = int(round(src_w * scale))
    scaled = src_img.resize((scaled_w, target_h), Image.Resampling.LANCZOS)
    excess_w = scaled_w - target_w
    return scaled.crop((excess_w, 0, scaled_w, target_h))


def render_32x9(src_img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Crop vertically to 32:9 aspect ratio and scale to target dimensions."""
    src_w, src_h = src_img.size
    crop_h = int(round(src_w * 9 / 32))
    crop_y = max(0, (src_h - crop_h) // 2)
    cropped = src_img.crop((0, crop_y, src_w, crop_y + crop_h))
    return cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)


def build_variant_wallpapers(variant_key: str, repo_root: str) -> list[str]:
    """Generate all target wallpaper PNGs for a given variant."""
    var_info = VARIANTS[variant_key]
    prefix = var_info["prefix"]
    wallpapers_dir = os.path.join(repo_root, "Wallpapers")
    sources_dir = os.path.join(wallpapers_dir, "sources")

    src_16x9_path = os.path.join(sources_dir, f"{prefix}-master-16x9.jpg")
    src_pano_path = os.path.join(sources_dir, f"{prefix}-master-pano.jpg")

    if not os.path.exists(src_16x9_path) or not os.path.exists(src_pano_path):
        raise FileNotFoundError(f"Missing source masters for {variant_key}")

    img_16x9 = Image.open(src_16x9_path).convert("RGB")
    img_pano = Image.open(src_pano_path).convert("RGB")

    generated = []
    for res_name, target_w, target_h, _ in TARGET_RESOLUTIONS:
        dest_filename = f"{prefix}-abstract-{res_name}.png"
        dest_path = os.path.join(wallpapers_dir, dest_filename)

        if "32:9" in _ or target_w / target_h > 2.5:
            rendered = render_32x9(img_pano, target_w, target_h)
        else:
            rendered = render_16x9(img_16x9, target_w, target_h)

        rendered.save(dest_path, format="PNG", optimize=True)
        generated.append(dest_path)
        print(f"  built {dest_filename} ({rendered.size[0]}x{rendered.size[1]})")

    return generated


def verify_wallpapers(repo_root: str) -> bool:
    """Verify presence and dimensions of all target wallpapers."""
    wallpapers_dir = os.path.join(repo_root, "Wallpapers")
    all_ok = True

    for var_key, var_info in VARIANTS.items():
        prefix = var_info["prefix"]
        for res_name, target_w, target_h, desc in TARGET_RESOLUTIONS:
            filename = f"{prefix}-abstract-{res_name}.png"
            path = os.path.join(wallpapers_dir, filename)

            if not os.path.exists(path):
                print(f"  FAIL: missing {filename}")
                all_ok = False
                continue

            try:
                im = Image.open(path)
                if im.size != (target_w, target_h):
                    print(f"  FAIL: {filename} size {im.size} != expected ({target_w}, {target_h})")
                    all_ok = False
                else:
                    print(f"  OK   {filename} ({target_w}x{target_h}, {desc})")
            except Exception as exc:
                print(f"  FAIL: {filename} read error: {exc}")
                all_ok = False

    return all_ok


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify generated wallpapers")
    parser.add_argument("--variant", choices=list(VARIANTS.keys()), help="Build specific variant")
    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    if args.check:
        print("verifying wallpapers...")
        ok = verify_wallpapers(repo_root)
        if not ok:
            sys.exit(1)
        print("all wallpapers present and verified")
        return

    targets = [args.variant] if args.variant else list(VARIANTS.keys())
    for var in targets:
        print(f"generating wallpapers for {VARIANTS[var]['title']}...")
        build_variant_wallpapers(var, repo_root)

    print("all wallpapers generated successfully.")


if __name__ == "__main__":
    main()
