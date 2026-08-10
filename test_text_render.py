import os, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
OUT_DIR = BASE_DIR / "output_test"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Canvas 1920x1080
base_img = Image.open(ASSETS_DIR / "woman_base.png").convert("RGBA")
canvas = base_img.resize((1920, 1080), Image.Resampling.LANCZOS)
draw = ImageDraw.Draw(canvas)

YELLOW = (255, 215, 0)      # Bright vibrant yellow #FFD700
WHITE = (255, 255, 255)
MUTED_WHITE = (220, 225, 235)
DARK_BG = (10, 10, 15)

def load_font(size, bold=True):
    fonts_to_try = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/trebucbd.ttf",
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/arial.ttf"
    ]
    for p in fonts_to_try:
        if Path(p).exists():
            try: return ImageFont.truetype(p, size)
            except: continue
    return ImageFont.load_default()

def draw_styled_text_block(canvas, text, tagline, center_x=1300, center_y=540, main_font_size=76, tagline_font_size=32):
    """
    Renders main sentence in middle-right of frame (x: ~750 to 1850).
    Words inside **word** are rendered in YELLOW, others in WHITE.
    Adds soft drop shadow for ultra crisp readability.
    """
    draw = ImageDraw.Draw(canvas)
    main_font = load_font(main_font_size, bold=True)
    tagline_font = load_font(tagline_font_size, bold=False)
    
    # Process tokens: parse **highlight**
    pattern = r'(\*\*.*?\*\*)'
    parts = re.split(pattern, text)
    tokens = []
    for p in parts:
        if p.startswith('**') and p.endswith('**'):
            tokens.append((p[2:-2], True))
        elif p:
            tokens.append((p, False))
            
    # Breakdown into words with space tokens
    words_list = []
    for chunk, is_yellow in tokens:
        words = chunk.split(' ')
        for i, w in enumerate(words):
            if w:
                words_list.append((w, is_yellow))
            if i < len(words) - 1:
                words_list.append((' ', False))

    # Wrap lines within max_width
    max_w = 1050  # Right side area width (from x=750 to 1800)
    lines = []
    curr_line = []
    curr_w = 0

    for word, is_yellow in words_list:
        w_box = draw.textbbox((0, 0), word, font=main_font)
        w_len = w_box[2] - w_box[0]

        if curr_w + w_len <= max_w or not curr_line:
            curr_line.append((word, is_yellow, w_len))
            curr_w += w_len
        else:
            if curr_line and curr_line[-1][0] == ' ':
                curr_w -= curr_line[-1][2]
                curr_line.pop()
            lines.append((curr_line, curr_w))
            if word == ' ':
                curr_line = []
                curr_w = 0
            else:
                curr_line = [(word, is_yellow, w_len)]
                curr_w = w_len

    if curr_line:
        if curr_line[-1][0] == ' ':
            curr_w -= curr_line[-1][2]
            curr_line.pop()
        lines.append((curr_line, curr_w))

    line_h = main_font_size + 24
    total_h = len(lines) * line_h + 80  # extra room for tagline
    start_y = center_y - total_h // 2

    # Draw dark shadow layer behind text
    shadow_layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow_layer)

    for l_idx, (line_words, line_w) in enumerate(lines):
        start_x = center_x - line_w // 2
        cur_x = start_x
        cur_y = start_y + l_idx * line_h

        for word, is_yellow, w_len in line_words:
            # Shadow
            sdraw.text((cur_x + 4, cur_y + 4), word, fill=(0, 0, 0, 200), font=main_font)
            cur_x += w_len

    # Blur shadow layer slightly
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(3))
    canvas.paste(shadow_layer, (0, 0), shadow_layer)

    # Draw foreground crisp text
    draw = ImageDraw.Draw(canvas)
    for l_idx, (line_words, line_w) in enumerate(lines):
        start_x = center_x - line_w // 2
        cur_x = start_x
        cur_y = start_y + l_idx * line_h

        for word, is_yellow, w_len in line_words:
            color = YELLOW if is_yellow else WHITE
            draw.text((cur_x, cur_y), word, fill=color, font=main_font)
            cur_x += w_len

    # Render Tagline line underneath (e.g. Learn English • Think Better • Speak Confidently)
    tag_y = start_y + len(lines) * line_h + 30
    
    # Parse bullet points in tagline for yellow accent
    tag_parts = tagline.split(" • ")
    tag_tokens = []
    for idx, tp in enumerate(tag_parts):
        # highlight specific words in yellow if needed
        is_highlight = "Think" in tp or "Better" in tp
        tag_tokens.append((tp, is_highlight))
        if idx < len(tag_parts) - 1:
            tag_tokens.append((" • ", True))

    # Calculate tagline width
    tag_total_w = 0
    measured_tokens = []
    for t_text, t_yellow in tag_tokens:
        tb = draw.textbbox((0, 0), t_text, font=tagline_font)
        tw = tb[2] - tb[0]
        measured_tokens.append((t_text, t_yellow, tw))
        tag_total_w += tw

    tag_start_x = center_x - tag_total_w // 2
    tag_cur_x = tag_start_x

    # Draw tagline shadow
    for t_text, t_yellow, tw in measured_tokens:
        draw.text((tag_cur_x + 2, tag_y + 2), t_text, fill=(0, 0, 0, 180), font=tagline_font)
        tag_cur_x += tw

    # Draw tagline foreground
    tag_cur_x = tag_start_x
    for t_text, t_yellow, tw in measured_tokens:
        col = YELLOW if t_yellow else MUTED_WHITE
        draw.text((tag_cur_x, tag_y), t_text, fill=col, font=tagline_font)
        tag_cur_x += tw

# Render sample sentence matching reference image 1 style!
test_text = "in a way **that** feels"
test_tagline = "Learn English • Think Better • Speak Confidently"

draw_styled_text_block(canvas, test_text, test_tagline)

out_path = OUT_DIR / "sample_rendered_frame.png"
canvas.convert("RGB").save(out_path)
print(f"Rendered sample frame to {out_path}")
