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
    woman_base_path = ASSETS_DIR / "woman_base.png"
    if woman_base_path.exists():
        base_img = Image.open(woman_base_path).convert("RGBA")
        canvas = base_img.resize((1920, 1080), Image.Resampling.LANCZOS)
    else:
        canvas = Image.new("RGBA", (1920, 1080), DARK_BG)

    gradient = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(gradient)
    for x in range(700, 1920):
        alpha = int(230 * ((x - 700) / 1220) ** 1.2)
        gdraw.line([(x, 0), (x, 1080)], fill=(5, 5, 12, alpha))
    canvas = Image.alpha_composite(canvas, gradient)

    draw = ImageDraw.Draw(canvas)

    # STRICT text box - ONLY right side, never overlaps woman, never crops right
    text_area_left = 790      # woman is on the left, never go past this
    text_area_right = 1870    # safe margin from right edge
    max_line_w = text_area_right - text_area_left
    text_area_width = max_line_w

    keyword_upper = highlight_word.upper() if highlight_word else ""
    words = main_title.upper().split()

    def wrap_words(font):
        lines = []
        curr = []
        for w in words:
            test = curr + [w]
            wb = draw.textbbox((0, 0), " ".join(test), font=font)
            tw = wb[2] - wb[0]
            if tw > max_line_w and curr:
                lines.append(curr)
                curr = [w]
            else:
                curr.append(w)
        if curr:
            lines.append(curr)
        return lines

    # Auto-fit: shrink font until text fits in <=3 lines, each line fits width
    font_size = 110
    lines = None
    while font_size >= 40:
        font = load_bold_font(font_size)
        lines = wrap_words(font)
        ok = len(lines) <= 3 and all(
            (draw.textbbox((0, 0), " ".join(l), font=font)[2]) <= max_line_w for l in lines
        )
        if ok:
            break
        font_size -= 5

    if lines is None:
        font = load_bold_font(45)
        lines = wrap_words(font)

    line_h = int(font_size * 1.3)
    total_h = len(lines) * line_h
    start_y = 500 - total_h // 2

    # Draw each line - CENTERED within the right-side text box
    text_center_x = (text_area_left + text_area_right) // 2

    for idx, line_words in enumerate(lines):
        line_str = " ".join(line_words)
        has_keyword = any(w == keyword_upper for w in line_words)

        wb = draw.textbbox((0, 0), line_str, font=font)
        lw = wb[2] - wb[0]
        # Center within the box, then clamp so it never crosses the box bounds
        lx = text_center_x - lw // 2
        lx = max(text_area_left, min(lx, text_area_right - lw))
        ly = start_y + idx * line_h

        # Shadow
        shadow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(shadow)
        for dx, dy in [(-4, -4), (4, -4), (-4, 4), (4, 4), (0, 8), (8, 0)]:
            sdraw.text((lx + dx, ly + dy), line_str, fill=(0, 0, 0, 255), font=font)
        shadow = shadow.filter(ImageFilter.GaussianBlur(6))
        canvas.paste(shadow, (0, 0), shadow)

        draw = ImageDraw.Draw(canvas)
        color = YELLOW if has_keyword else WHITE
        draw.text((lx, ly), line_str, fill=color, font=font, stroke_width=5, stroke_fill=BLACK)

    # EP pill bottom right
    font_pill = load_bold_font(36)
    pill_text = f"EP {ep_num}"
    pb = draw.textbbox((0, 0), pill_text, font=font_pill)
    pw = pb[2] - pb[0]
    px = 1920 - pw - 80
    py = 960
    draw.rounded_rectangle([(px - 20, py - 10), (px + pw + 20, py + 50)], radius=12, fill=(255, 215, 0, 220))
    draw.text((px, py), pill_text, fill=BLACK, font=font_pill)

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
