import os, re, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output" / "thumbnails"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

YELLOW = (255, 215, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BG = (10, 10, 15)

def load_bold_font(size):
    fonts_to_try = [
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/ariblk.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    ]
    for p in fonts_to_try:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except:
                continue
    return ImageFont.load_default()

def create_thumbnail(main_title, highlight_word="", subtitle="", ep_num=1, output_name="thumbnail.png", output_dir=None):
    """
    CLEAN YouTube thumbnail - just background + 1 big bold word + episode pill.
    No crowding, no extra text.
    """
    woman_base_path = ASSETS_DIR / "woman_base.png"
    if woman_base_path.exists():
        base_img = Image.open(woman_base_path).convert("RGBA")
        canvas = base_img.resize((1920, 1080), Image.Resampling.LANCZOS)
    else:
        canvas = Image.new("RGBA", (1920, 1080), DARK_BG)

    # Dark gradient overlay on right side for text legibility
    gradient_overlay = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(gradient_overlay)
    for x in range(700, 1920):
        alpha = int(200 * ((x - 700) / 1220) ** 1.3)
        gdraw.line([(x, 0), (x, 1080)], fill=(5, 5, 12, alpha))
    canvas = Image.alpha_composite(canvas, gradient_overlay)

    draw = ImageDraw.Draw(canvas)

    # ONE big bold keyword - center right
    font_huge = load_bold_font(160)
    keyword = highlight_word.upper() if highlight_word else main_title.split()[0].upper()

    kb = draw.textbbox((0, 0), keyword, font=font_huge)
    kw = kb[2] - kb[0]
    kh = kb[3] - kb[1]

    kx = 1300 - kw // 2
    ky = 440

    # Heavy shadow for pop
    shadow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    for dx, dy in [(-5, -5), (5, -5), (-5, 5), (5, 5), (0, 10), (10, 0)]:
        sdraw.text((kx + dx, ky + dy), keyword, fill=(0, 0, 0, 255), font=font_huge)
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    canvas.paste(shadow, (0, 0), shadow)

    # Foreground keyword
    draw = ImageDraw.Draw(canvas)
    draw.text((kx, ky), keyword, fill=YELLOW, font=font_huge, stroke_width=5, stroke_fill=BLACK)

    # Small episode pill bottom right
    font_pill = load_bold_font(36)
    pill_text = f"EP {ep_num}"
    pb = draw.textbbox((0, 0), pill_text, font=font_pill)
    pw = pb[2] - pb[0]
    pill_x = 1920 - pw - 80
    pill_y = 960
    draw.rounded_rectangle([(pill_x - 20, pill_y - 10), (pill_x + pw + 20, pill_y + 50)], radius=12, fill=(255, 215, 0, 220))
    draw.text((pill_x, pill_y), pill_text, fill=BLACK, font=font_pill)

    # Save
    if output_dir:
        out_file = Path(output_dir) / output_name
    else:
        out_file = OUTPUT_DIR / output_name
    canvas.convert("RGB").save(out_file, quality=95)
    print(f"Thumbnail saved: {out_file}")
    return out_file

if __name__ == "__main__":
    create_thumbnail("THINK IN ENGLISH", "THINK", ep_num=1, output_name="thumb_think.png")
    create_thumbnail("SPEAK WITH CONFIDENCE", "CONFIDENCE", ep_num=2, output_name="thumb_confidence.png")
    create_thumbnail("MASTER DAILY HABITS", "HABITS", ep_num=3, output_name="thumb_habits.png")
