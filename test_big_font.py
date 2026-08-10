import os, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
OUT_DIR = BASE_DIR / "output_test"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Load base image
base_img_path = ASSETS_DIR / "woman_base.png"
base_img = Image.open(base_img_path).convert("RGBA")
canvas = base_img.resize((1920, 1080), Image.Resampling.LANCZOS)
draw = ImageDraw.Draw(canvas)

YELLOW = (255, 215, 0)         # Bright vibrant yellow #FFD700
WHITE = (255, 255, 255)
MUTED_WHITE = (220, 225, 235)
DARK_BAR = (20, 25, 40)

def load_font(size, bold=True):
    fonts_to_try = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/trebucbd.ttf",
        "C:/Windows/Fonts/impact.ttf"
    ]
    for p in fonts_to_try:
        if Path(p).exists():
            try: return ImageFont.truetype(p, size)
            except: continue
    return ImageFont.load_default()

def draw_audio_waves(draw, start_x, start_y):
    """Draws sleek animated audio waveform bars on top left tab."""
    heights = [14, 28, 20, 36, 24, 16]
    for i, h in enumerate(heights):
        x = start_x + i * 8
        draw.rounded_rectangle([(x, start_y - h//2), (x + 4, start_y + h//2)], radius=2, fill=YELLOW)

def draw_big_2line_text(canvas, text, speaker="EMMA"):
    draw = ImageDraw.Draw(canvas)
    
    # 1. Top Left Header Tab (With audio waves & flag glyph)
    font_tab = load_font(28, bold=True)
    draw.rounded_rectangle([(60, 45), (460, 105)], radius=15, fill=DARK_BAR, outline=YELLOW, width=2)
    draw_audio_waves(draw, 90, 75)
    draw.text((160, 75), "SLOW ENGLISH", fill=WHITE, font=font_tab, anchor="lm")
    draw.text((365, 75), "🇬🇧", fill=WHITE, font=font_tab, anchor="lm")

    # 2. Top Right Speaker Pill & Episode Badge
    font_speaker = load_font(28, bold=True)
    draw.rounded_rectangle([(1580, 45), (1860, 105)], radius=15, fill=DARK_BAR, outline=YELLOW, width=2)
    draw.text((1720, 75), f"🎙️ {speaker}", fill=YELLOW, font=font_speaker, anchor="mm")

    # 3. HUGE 2-LINE TEXT (Font Size: 100px)
    font_main = load_font(100, bold=True)
    
    # Parse **highlight**
    pattern = r'(\*\*.*?\*\*)'
    parts = re.split(pattern, text)
    words_list = []
    for p in parts:
        if p.startswith('**') and p.endswith('**'):
            words_list.append((p[2:-2], True))
        elif p:
            for w in p.split(' '):
                if w: words_list.append((w, False))

    # Strict 2-line max wrapping (Right side center x=1300, y=540)
    max_w = 1050
    lines = []
    curr_line = []
    curr_w = 0

    for word, is_yellow in words_list:
        wb = draw.textbbox((0, 0), word, font=font_main)
        wl = wb[2] - wb[0] + 24
        if curr_w + wl <= max_w or not curr_line:
            curr_line.append((word, is_yellow, wl))
            curr_w += wl
        else:
            lines.append((curr_line, curr_w))
            curr_line = [(word, is_yellow, wl)]
            curr_w = wl
    if curr_line:
        lines.append((curr_line, curr_w))

    # Keep strictly 1 or 2 lines
    if len(lines) > 2:
        # Re-wrap into 2 lines
        mid = len(words_list) // 2
        l1, l2 = words_list[:mid], words_list[mid:]
        
        def calc_line(w_list):
            w_total = 0
            res = []
            for w, y in w_list:
                wb = draw.textbbox((0, 0), w, font=font_main)
                wl = wb[2] - wb[0] + 24
                res.append((w, y, wl))
                w_total += wl
            return res, w_total

        line1, w1 = calc_line(l1)
        line2, w2 = calc_line(l2)
        lines = [(line1, w1), (line2, w2)]

    center_x = 1300
    center_y = 540
    line_h = 130
    total_h = len(lines) * line_h
    start_y = center_y - total_h // 2

    # Shadow Layer
    shadow_layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow_layer)
    for l_idx, (line_words, line_w) in enumerate(lines):
        start_x = center_x - line_w // 2
        cur_x = start_x
        cur_y = start_y + l_idx * line_h
        for word, is_yellow, wl in line_words:
            sdraw.text((cur_x + 6, cur_y + 6), word, fill=(0, 0, 0, 240), font=font_main)
            cur_x += wl
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(4))
    canvas.paste(shadow_layer, (0, 0), shadow_layer)

    # Foreground HUGE Text
    draw = ImageDraw.Draw(canvas)
    for l_idx, (line_words, line_w) in enumerate(lines):
        start_x = center_x - line_w // 2
        cur_x = start_x
        cur_y = start_y + l_idx * line_h
        for word, is_yellow, wl in line_words:
            col = YELLOW if is_yellow else WHITE
            draw.text((cur_x, cur_y), word, fill=col, font=font_main)
            cur_x += wl

    # 4. Bottom Footer & Progress Bar
    draw.line([(0, 1025), (1920, 1025)], fill=(40, 45, 60), width=2)
    draw.line([(0, 1025), (800, 1025)], fill=YELLOW, width=5)

    font_footer = load_font(24, bold=False)
    draw.text((70, 1052), "🎧 Slow & Clear English for Beginners", fill=MUTED_WHITE, font=font_footer, anchor="lm")
    draw.text((1850, 1052), "05:12 / 30:00", fill=YELLOW, font=font_footer, anchor="rm")

    out_file = OUT_DIR / "sample_huge_2line_text.png"
    canvas.convert("RGB").save(out_file)
    print("Saved sample_huge_2line_text.png")

draw_big_2line_text(canvas, "in a way **that** feels", "EMMA")
