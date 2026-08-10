import os, re, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output" / "thumbnails"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

YELLOW = (255, 215, 0)       # #FFD700 Vibrant Yellow
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BG = (10, 10, 15)

def load_bold_font(size):
    """
    Loads ultra-bold thumbnail fonts (prioritizing Impact and Arial Black / Bold).
    """
    fonts_to_try = [
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/ariblk.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/trebucbd.ttf"
    ]
    for p in fonts_to_try:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except:
                continue
    return ImageFont.load_default()

def create_thumbnail(main_title, highlight_word="", subtitle="", ep_num=1, output_name="thumbnail.png"):
    """
    Creates a clean, bold, high-CTR YouTube thumbnail (1920x1080).
    Focuses strictly on background studio image + massive bold, punchy text.
    Removed unnecessary badges, episode numbers, and clutter.
    """
    woman_base_path = ASSETS_DIR / "woman_base.png"
    if woman_base_path.exists():
        base_img = Image.open(woman_base_path).convert("RGBA")
        canvas = base_img.resize((1920, 1080), Image.Resampling.LANCZOS)
    else:
        canvas = Image.new("RGBA", (1920, 1080), DARK_BG)

    # Apply a subtle dark gradient/shadow overlay on the right side for maximum text legibility
    gradient_overlay = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(gradient_overlay)
    for x in range(800, 1920):
        alpha = int(180 * ((x - 800) / 1120) ** 1.2)
        gdraw.line([(x, 0), (x, 1080)], fill=(5, 5, 12, alpha))
    canvas = Image.alpha_composite(canvas, gradient_overlay)

    draw = ImageDraw.Draw(canvas)

    # Main Title Rendering (Ultra-bold, size 120px)
    font_title = load_bold_font(120)

    # Format text with yellow highlight
    formatted_title = main_title.strip()
    if highlight_word and highlight_word in formatted_title and f"**{highlight_word}**" not in formatted_title:
        formatted_title = formatted_title.replace(highlight_word, f"**{highlight_word}**")

    # Split into words
    pattern = r'(\*\*.*?\*\*)'
    parts = re.split(pattern, formatted_title)
    words_list = []
    for p in parts:
        if p.startswith('**') and p.endswith('**'):
            words_list.append((p[2:-2].upper(), True))
        elif p:
            for w in p.split(' '):
                if w:
                    words_list.append((w.upper(), False))

    # Wrap words into maximum 2-3 lines for high visual impact
    lines = []
    curr_line = []
    curr_w = 0
    max_w = 950

    for word, is_yellow in words_list:
        wb = draw.textbbox((0, 0), word, font=font_title)
        wl = wb[2] - wb[0] + 28  # word width + spacing
        if curr_w + wl <= max_w or not curr_line:
            curr_line.append((word, is_yellow, wl))
            curr_w += wl
        else:
            lines.append((curr_line, curr_w))
            curr_line = [(word, is_yellow, wl)]
            curr_w = wl
    if curr_line:
        lines.append((curr_line, curr_w))

    center_x = 1350
    center_y = 540
    line_h = 140
    total_h = len(lines) * line_h
    start_y = center_y - total_h // 2

    # Heavy Blurred Drop-Shadow Layer for text pop
    shadow_layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow_layer)

    for l_idx, (line_words, line_w) in enumerate(lines):
        start_x = center_x - line_w // 2
        cur_x = start_x
        cur_y = start_y + l_idx * line_h

        for word, is_yellow, wl in line_words:
            # Draw multi-offset heavy black shadow
            for dx, dy in [(-4, -4), (4, -4), (-4, 4), (4, 4), (0, 8), (8, 0)]:
                sdraw.text((cur_x + dx, cur_y + dy), word, fill=(0, 0, 0, 255), font=font_title)
            cur_x += wl

    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(6))
    canvas.paste(shadow_layer, (0, 0), shadow_layer)

    # Foreground Ultra-Bold Text with sharp black outline
    draw = ImageDraw.Draw(canvas)
    for l_idx, (line_words, line_w) in enumerate(lines):
        start_x = center_x - line_w // 2
        cur_x = start_x
        cur_y = start_y + l_idx * line_h

        for word, is_yellow, wl in line_words:
            col = YELLOW if is_yellow else WHITE
            # Outline stroke for crisp contrast
            draw.text((cur_x, cur_y), word, fill=col, font=font_title, stroke_width=4, stroke_fill=BLACK)
            cur_x += wl

    # Save
    out_file = OUTPUT_DIR / output_name
    canvas.convert("RGB").save(out_file, quality=95)
    print(f"Bold thumbnail saved: {out_file}")
    return out_file

if __name__ == "__main__":
    create_thumbnail("THINK IN ENGLISH", "THINK", output_name="clean_thumbnail_1.png")
    create_thumbnail("SPEAK WITH CONFIDENCE", "CONFIDENCE", output_name="clean_thumbnail_2.png")
    create_thumbnail("MASTER DAILY HABITS", "HABITS", output_name="clean_thumbnail_3.png")
