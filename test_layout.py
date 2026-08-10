import os, sys, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Copy provided source images to assets folder for self-contained structure
src_bg = Path(r"C:\Users\kreg9\Downloads\ChatGPT Image Aug 9, 2026, 11_46_01 AM.png")
src_woman_base = Path(r"C:\Users\kreg9\Downloads\ChatGPT Image Aug 9, 2026, 11_37_48 AM.png")
src_layer_woman = Path(r"C:\Users\kreg9\Downloads\layer-woman.png")
src_style_ref = Path(r"C:\Users\kreg9\Downloads\ChatGPT Image Aug 9, 2026, 11_44_13 AM.png")

if src_bg.exists(): shutil.copy(src_bg, ASSETS_DIR / "background.png")
if src_woman_base.exists(): shutil.copy(src_woman_base, ASSETS_DIR / "woman_base.png")
if src_layer_woman.exists(): shutil.copy(src_layer_woman, ASSETS_DIR / "layer_woman.png")
if src_style_ref.exists(): shutil.copy(src_style_ref, ASSETS_DIR / "style_reference.png")

print("Assets copied successfully!")

# Inspect base image dimensions
base_img_path = ASSETS_DIR / "woman_base.png"
if base_img_path.exists():
    img = Image.open(base_img_path)
    print(f"Woman base image size: {img.size}, mode: {img.mode}")
