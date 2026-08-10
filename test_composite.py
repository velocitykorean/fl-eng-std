import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
OUT_DIR = BASE_DIR / "output_test"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Load images
bg_img = Image.open(ASSETS_DIR / "background.png").convert("RGBA")
woman_base = Image.open(ASSETS_DIR / "woman_base.png").convert("RGBA")

print("BG size:", bg_img.size)
print("Woman base size:", woman_base.size)

# Method 1: Resize woman_base to 1920x1080 (preserving 16:9 ratio)
canvas1 = Image.new("RGBA", (1920, 1080), (11, 14, 27, 255))
woman_base_resized = woman_base.resize((1920, 1080), Image.Resampling.LANCZOS)
canvas1.paste(woman_base_resized, (0, 0))

canvas1.convert("RGB").save(OUT_DIR / "method1_base_resized.png")
print("Saved method1_base_resized.png")

# Method 2: Layer woman over background
# If layer_woman has transparent background
if (ASSETS_DIR / "layer_woman.png").exists():
    layer_w = Image.open(ASSETS_DIR / "layer_woman.png").convert("RGBA")
    print("Layer woman size:", layer_w.size)
    bg_resized = bg_img.resize((1920, 1080), Image.Resampling.LANCZOS)
    
    # Scale layer woman to fit left height
    aspect = layer_w.width / layer_w.height
    new_h = 1080
    new_w = int(new_h * aspect)
    layer_w_resized = layer_w.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    canvas2 = bg_resized.copy()
    canvas2.paste(layer_w_resized, (0, 0), layer_w_resized)
    canvas2.convert("RGB").save(OUT_DIR / "method2_layer_composite.png")
    print("Saved method2_layer_composite.png")
