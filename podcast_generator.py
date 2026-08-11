"""
SLOW AMERICAN ENGLISH PODCAST GENERATOR - FULL 30-MINUTE BROADCAST
Features:
- 100% Native Edge TTS Microsoft Neural Voices:
  * Host 1 (Emma): en-US-AvaNeural (Ultra-realistic US Female Neural)
  * Host 2 (Andrew): en-US-AndrewNeural (Ultra-realistic US Male Neural)
- Distinct voice switching per turn with matching speaker badges
- Continuous animated pulsing audio wave bars on top-left tab
- HUGE 100px 2-line text with vibrant yellow keyword highlights
"""
import os, sys, json, math, subprocess, random, requests, re, asyncio
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from dotenv import load_dotenv
import edge_tts

load_dotenv()

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Video Specs
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 30

# Colors
YELLOW = (255, 215, 0)         # #FFD700 Vibrant Yellow
WHITE = (255, 255, 255)
MUTED_WHITE = (220, 225, 235)
DARK_BG = (10, 10, 15)
DARK_BAR = (20, 25, 40)
# Channel Branding
CHANNEL_NAME = "ENGLISH FLUENCY STUDIO"

# Edge TTS Neural Voices
EMMA_VOICE = "en-US-AvaNeural"
ANDREW_VOICE = "en-US-AndrewNeural"
VOICE_RATE = "-15%"

# Topics List
TOPICS = [
    {"topic": "How to Think Directly in American English Without Translating", "keyword": "THINK", "sub": "STOP TRANSLATING IN YOUR HEAD"},
    {"topic": "Building Confidence to Speak American English Everyday", "keyword": "CONFIDENCE", "sub": "SPEAK WITHOUT FEAR"},
    {"topic": "The Power of Daily American English Listening Habits", "keyword": "HABITS", "sub": "IMPROVE YOUR LISTENING FAST"},
    {"topic": "Overcoming the Fear of Making Mistakes in American English", "keyword": "MISTAKES", "sub": "LEARN FROM EVERY MISTAKE"},
    {"topic": "How to Learn American English Vocabulary Naturally", "keyword": "VOCABULARY", "sub": "REMEMBER WORDS EASILY"},
    {"topic": "Small Talk and Everyday American English Conversations", "keyword": "CONVERSATIONS", "sub": "SPEAK NATURALLY IN ANY SITUATION"},
    {"topic": "Mastering American Accent Pronunciation and Rhythm", "keyword": "PRONUNCIATION", "sub": "SOUND MORE NATURAL"},
    {"topic": "Traveling in the USA and Exploring American Culture", "keyword": "TRAVELING", "sub": "AMERICAN ENGLISH FOR TRAVEL"},
    {"topic": "Work, Business, and Professional American English Basics", "keyword": "CAREER", "sub": "BOOST YOUR PROFESSIONAL ENGLISH"},
    {"topic": "The Secret to Fluency: Consistency Over Perfection", "keyword": "FLUENCY", "sub": "THE PATH TO REAL FLUENCY"}
]

def load_font(size, bold=True):
    fonts_to_try = [
        # Windows fonts
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/trebucbd.ttf",
        "C:/Windows/Fonts/impact.ttf",
        # Linux fonts (Ubuntu/GitHub Actions)
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    ]
    for p in fonts_to_try:
        if Path(p).exists():
            try: return ImageFont.truetype(p, size)
            except: continue
    return ImageFont.load_default()

def clean_text(text):
    text = re.sub(r'\b(mm+|um+|uh+|ah+)\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def generate_script(topic_item, target_turns=130):
    topic_str = topic_item["topic"]
    print(f"Generating full 30-minute American English script for: '{topic_str}' ({target_turns} turns)...")

    prompt = f"""Generate a full 30-minute Slow American English Podcast script for English learners.
Topic: {topic_str}

HOSTS strictly alternate:
- Emma (Host1): Primary American female host & teacher.
- Andrew (Host2): American male co-host.

REQUIREMENTS:
1. Each turn MUST be short (1 sentence, 6-12 words) so it fits in HUGE 2-line text on screen!
2. Use standard American English vocabulary and natural expressions.
3. Wrap exactly 1 key word per turn in double asterisks like **keyword**.
4. Output EXACTLY {target_turns} turns as a clean JSON array:
[
  {{"speaker": "Host1", "text": "Welcome to **American English** Podcast."}},
  {{"speaker": "Host2", "text": "Today we discuss how to **think** in English."}}
]"""

    POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")
    headers = {"Authorization": f"Bearer {POLLINATIONS_API_KEY}"}
    for attempt in range(3):
        try:
            resp = requests.post("https://gen.pollinations.ai/v1/chat/completions", json={
                "model": "gemini-fast",
                "messages": [
                    {"role": "system", "content": "You write short 1-sentence American English podcast turns for ESL learners. Wrap 1 key word per turn in **keyword**."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.85
            }, headers=headers, timeout=180)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"].strip()
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            script = json.loads(content)
            for i, turn in enumerate(script):
                turn["speaker"] = "Host1" if i % 2 == 0 else "Host2"
                turn["text"] = clean_text(turn["text"])
                if "**" not in turn["text"]:
                    words = turn["text"].split()
                    if len(words) > 1:
                        idx = len(words) // 2
                        words[idx] = f"**{words[idx]}**"
                        turn["text"] = " ".join(words)
            print(f"Script generated successfully: {len(script)} turns.")

            # Pad script to target length if needed
            if len(script) < target_turns:
                fallback = _fallback_script(topic_str, target_turns)
                needed = target_turns - len(script)
                script.extend(fallback[:needed])
                print(f"Padded script to {len(script)} turns.")

            return script
        except Exception as e:
            print(f"Script attempt {attempt+1} error: {e}")
    
    return _fallback_script(topic_str, target_turns)

def _fallback_script(topic_str, target_turns=130):
    script = []
    for i in range(target_turns):
        s = "Host1" if i % 2 == 0 else "Host2"
        if s == "Host1":
            script.append({"speaker": "Host1", "text": f"Welcome to **American English** Podcast."})
        else:
            script.append({"speaker": "Host2", "text": f"Let us master **{topic_str}** together."})
    return script

async def generate_audio_edge(turns, run_dir):
    """
    Generates 100% NATIVE AMERICAN ENGLISH VOICE AUDIO via Edge TTS Neural:
    - Host 1 (Emma): en-US-AvaNeural (US Female Neural)
    - Host 2 (Andrew): en-US-AndrewNeural (US Male Neural)
    """
    audio_dir = run_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    audio_files = []

    print(f"Generating 100% NATIVE AMERICAN ENGLISH Edge TTS Neural audio for {len(turns)} turns...")
    for i, turn in enumerate(turns):
        mp3_path = audio_dir / f"audio_{i:04d}.mp3"
        spoken_text = re.sub(r'\*\*(.*?)\*\*', r'\1', turn["text"])
        
        target_voice = EMMA_VOICE if turn["speaker"] == "Host1" else ANDREW_VOICE
        voice_label = "Emma (en-US-AvaNeural)" if turn["speaker"] == "Host1" else "Andrew (en-US-AndrewNeural)"
        
        generated = False
        for attempt in range(3):
            try:
                communicate = edge_tts.Communicate(spoken_text, target_voice, rate=VOICE_RATE)
                await communicate.save(str(mp3_path))
                if mp3_path.exists() and mp3_path.stat().st_size > 0:
                    generated = True
                    break
            except Exception as e:
                print(f"  Edge TTS turn {i} attempt {attempt+1} error: {e}")
                await asyncio.sleep(1)

        if not generated:
            print(f"  Warning: Falling back to silent audio for turn {i}")
            subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "6", str(mp3_path)], capture_output=True)

        # Measure audio duration via ffprobe
        try:
            r = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(mp3_path)],
                capture_output=True, text=True
            )
            duration = float(r.stdout.strip()) if r.stdout else 6.0
        except:
            duration = 6.0

        audio_files.append({"path": str(mp3_path), "duration": duration, "speaker": turn["speaker"]})
        if (i + 1) % 25 == 0 or i == len(turns) - 1:
            print(f"  Audio {i+1}/{len(turns)} generated (Voice: {voice_label}).")

    return audio_files

def draw_animated_audio_waves(draw, start_x, start_y, frame_index=0):
    num_bars = 6
    for i in range(num_bars):
        h = int(24 + 14 * math.sin(frame_index * 0.6 + i * 1.1))
        x = start_x + i * 9
        draw.rounded_rectangle([(x, start_y - h//2), (x + 5, start_y + h//2)], radius=2, fill=YELLOW)

def draw_vector_mic(draw, center_x, center_y):
    draw.rounded_rectangle([(center_x - 6, center_y - 12), (center_x + 6, center_y + 4)], radius=4, fill=YELLOW)
    draw.arc([(center_x - 10, center_y - 4), (center_x + 10, center_y + 10)], start=0, end=180, fill=YELLOW, width=3)
    draw.line([(center_x, center_y + 10), (center_x, center_y + 16)], fill=YELLOW, width=3)
    draw.line([(center_x - 6, center_y + 16), (center_x + 6, center_y + 16)], fill=YELLOW, width=3)

def render_huge_frame(turn, current_idx, total_turns, elapsed_time, total_duration, output_path):
    woman_base_path = ASSETS_DIR / "woman_base.png"
    if woman_base_path.exists():
        base_img = Image.open(woman_base_path).convert("RGBA")
        canvas = base_img.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.LANCZOS)
    else:
        canvas = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), DARK_BG)

    draw = ImageDraw.Draw(canvas)

    # 1. Top Left Tab: Continuously Animated Audio Waves + Channel Name
    font_tab = load_font(32, bold=True)
    tb_tab = draw.textbbox((0, 0), CHANNEL_NAME, font=font_tab)
    tw_tab = tb_tab[2] - tb_tab[0]
    tab_right = max(520, 190 + tw_tab + 30)
    draw.rounded_rectangle([(60, 40), (tab_right, 110)], radius=18, fill=DARK_BAR, outline=YELLOW, width=3)
    draw_animated_audio_waves(draw, 90, 75, frame_index=current_idx)
    draw.text((180, 75), CHANNEL_NAME, fill=WHITE, font=font_tab, anchor="lm")

    # 2. Top Right Speaker Pill
    speaker_name = "EMMA" if turn["speaker"] == "Host1" else "ANDREW"
    font_speaker = load_font(30, bold=True)
    draw.rounded_rectangle([(1540, 40), (1880, 110)], radius=18, fill=DARK_BAR, outline=YELLOW, width=3)
    draw_vector_mic(draw, 1580, 75)
    draw.text((1620, 75), f"HOST: {speaker_name}", fill=YELLOW, font=font_speaker, anchor="lm")

    # 3. HUGE 2-LINE TEXT DISPLAY - CENTERED on right side, NO cropping
    font_main = load_font(75, bold=True)
    text = turn["text"]
    
    pattern = r'(\*\*.*?\*\*)'
    parts = re.split(pattern, text)
    words_list = []
    for p in parts:
        if p.startswith('**') and p.endswith('**'):
            words_list.append((p[2:-2], True))
        elif p:
            for w in p.split(' '):
                if w: words_list.append((w, False))

    # Text area: x=780 to x=1820 (safe zone, no cropping)
    text_area_left = 780
    text_area_right = 1820
    max_w = text_area_right - text_area_left  # 1040px
    text_center_x = (text_area_left + text_area_right) // 2  # 1300

    lines = []
    curr_line = []
    curr_w = 0

    for word, is_yellow in words_list:
        wb = draw.textbbox((0, 0), word, font=font_main)
        wl = wb[2] - wb[0] + 16
        if curr_w + wl <= max_w or not curr_line:
            curr_line.append((word, is_yellow, wl))
            curr_w += wl
        else:
            lines.append((curr_line, curr_w))
            curr_line = [(word, is_yellow, wl)]
            curr_w = wl
    if curr_line:
        lines.append((curr_line, curr_w))

    # Max 2 lines - if more, split evenly
    if len(lines) > 2:
        mid = len(words_list) // 2
        l1, l2 = words_list[:mid], words_list[mid:]
        def calc_line(w_list):
            w_total = 0
            res = []
            for w, y in w_list:
                wb = draw.textbbox((0, 0), w, font=font_main)
                wl = wb[2] - wb[0] + 16
                res.append((w, y, wl))
                w_total += wl
            return res, w_total
        line1, w1 = calc_line(l1)
        line2, w2 = calc_line(l2)
        lines = [(line1, w1), (line2, w2)]

    center_y = 520
    line_h = 120
    total_h = len(lines) * line_h
    start_y = center_y - total_h // 2

    # Blur Shadow
    shadow_layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow_layer)
    for l_idx, (line_words, line_w) in enumerate(lines):
        start_x = text_center_x - line_w // 2
        start_x = max(text_area_left, min(start_x, text_area_right - line_w))
        cur_x = start_x
        cur_y = start_y + l_idx * line_h
        for word, is_yellow, wl in line_words:
            sdraw.text((cur_x + 4, cur_y + 4), word, fill=(0, 0, 0, 240), font=font_main)
            cur_x += wl
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(4))
    canvas.paste(shadow_layer, (0, 0), shadow_layer)

    # Foreground Huge Text
    draw = ImageDraw.Draw(canvas)
    for l_idx, (line_words, line_w) in enumerate(lines):
        start_x = text_center_x - line_w // 2
        start_x = max(text_area_left, min(start_x, text_area_right - line_w))
        cur_x = start_x
        cur_y = start_y + l_idx * line_h
        for word, is_yellow, wl in line_words:
            col = YELLOW if is_yellow else WHITE
            draw.text((cur_x, cur_y), word, fill=col, font=font_main)
            cur_x += wl

    # 4. Bottom Footer & Progress Bar
    draw.line([(0, 1025), (VIDEO_WIDTH, 1025)], fill=(40, 45, 60), width=2)
    progress_ratio = min(1.0, elapsed_time / max(1.0, total_duration))
    bar_w = int(VIDEO_WIDTH * progress_ratio)
    draw.line([(0, 1025), (bar_w, 1025)], fill=YELLOW, width=5)

    font_footer = load_font(30, bold=False)
    draw.text((70, 1052), "Slow & Clear American English Accent", fill=MUTED_WHITE, font=font_footer, anchor="lm")
    
    min_str = f"{int(elapsed_time // 60):02d}:{int(elapsed_time % 60):02d} / {int(total_duration // 60):02d}:{int(total_duration % 60):02d}"
    draw.text((1850, 1052), min_str, fill=YELLOW, font=font_footer, anchor="rm")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_path, quality=92)

def assemble_video(turns, audio_files, run_dir):
    frames_dir = run_dir / "frames"
    clips_dir = run_dir / "clips"
    frames_dir.mkdir(parents=True, exist_ok=True)
    clips_dir.mkdir(parents=True, exist_ok=True)

    total_duration = sum(a["duration"] for a in audio_files)
    print(f"Building video clips ({len(turns)} turns, Total Duration: {total_duration/60:.1f} mins)...")

    clips = []
    elapsed_time = 0.0

    for i, (turn, audio) in enumerate(zip(turns, audio_files)):
        img_path = frames_dir / f"frame_{i:04d}.png"
        clip_path = clips_dir / f"clip_{i:04d}.mp4"

        render_huge_frame(turn, i, len(turns), elapsed_time, total_duration, str(img_path))

        dur_str = f"{audio['duration']:.3f}"
        subprocess.run([
            "ffmpeg", "-y", "-loop", "1", "-i", str(img_path), "-i", audio["path"],
            "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT},fps={FPS}",
            "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p", "-preset", "fast", "-t", dur_str, str(clip_path)
        ], check=True, capture_output=True)

        clips.append(clip_path)
        elapsed_time += audio["duration"]

        if (i + 1) % 25 == 0 or i == len(turns) - 1:
            print(f"  Clip {i+1}/{len(turns)} rendered.")

    concat_file = run_dir / "concat_list.txt"
    with open(concat_file, "w") as f:
        for c in clips:
            f.write(f"file '{c.resolve().as_posix()}'\n")

    final_video = run_dir / "podcast_30min_final.mp4"
    print(f"Concatenating into final video: {final_video.name}...")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(final_video)], check=True)

    return final_video, total_duration

async def run_full_generator(topic_index=0, custom_turns=360):
    topic_item = TOPICS[topic_index % len(TOPICS)]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_DIR / f"run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("  SLOW AMERICAN ENGLISH PODCAST GENERATOR (Edge TTS Neural)")
    print(f"  Topic: {topic_item['topic']}")
    print(f"  Target Turns: {custom_turns} (~30 Minutes)")
    print("=" * 70)

    turns = generate_script(topic_item, target_turns=custom_turns)
    with open(run_dir / "script.json", "w", encoding="utf-8") as f:
        json.dump({"topic": topic_item, "turns": turns}, f, indent=2)

    audio_files = await generate_audio_edge(turns, run_dir)
    final_video, duration = assemble_video(turns, audio_files, run_dir)

    from thumbnail_generator import create_thumbnail
    thumb_path = create_thumbnail(
        main_title=topic_item["topic"].upper(),
        highlight_word=topic_item["keyword"],
        subtitle="SLOW AMERICAN ENGLISH PODCAST",
        ep_num=random.randint(1, 99),
        output_name=f"thumbnail_{timestamp}.png",
        output_dir=str(run_dir)
    )

    # Generate AI-powered YouTube metadata for upload
    ep_num = random.randint(1, 999)
    topic_name = topic_item["topic"]
    keyword = topic_item["keyword"]

    print(f"  🤖 Generating AI-powered YouTube title & description...")
    metadata = generate_youtube_metadata_ai(topic_name, keyword, ep_num, duration, turns, run_dir)

    metadata_path = run_dir / "youtube_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"  📄 YouTube metadata saved: {metadata_path.name}")

    print("=" * 70)
    print("  FULL BROADCAST GENERATION COMPLETE!")
    print(f"  Video File: {final_video}")
    print(f"  Thumbnail: {thumb_path}")
    print(f"  Total Duration: {duration / 60:.1f} Minutes ({len(turns)} turns)")
    print(f"  YouTube Title: {metadata.get('selected_title', 'N/A')}")
    print("=" * 70)
    return final_video, thumb_path


def generate_youtube_metadata_ai(topic_name, keyword, ep_num, duration, turns, run_dir):
    """Generate viral YouTube title, description, and tags using Pollinations AI"""

    POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")
    if not POLLINATIONS_API_KEY:
        print("  ⚠️ POLLINATIONS_API_KEY not set, using fallback metadata")
        return _fallback_metadata(topic_name, keyword, ep_num, duration, turns)

    headers = {"Authorization": f"Bearer {POLLINATIONS_API_KEY}"}

    # Sample some turns for context - use actual script content
    sample_turns = turns[:15] if len(turns) > 15 else turns
    turn_texts = [f"{t['speaker']}: {t['text']}" for t in sample_turns]
    turns_preview = "\n".join(turn_texts)

    prompt = f"""Generate a VIRAL YouTube title, description, and tags for an English learning podcast video.

TOPIC: {topic_name}
KEYWORD: {keyword}
EPISODE NUMBER: {ep_num}
DURATION: {int(duration/60)} minutes
CHANNEL NAME: English Fluency Studio
HOSTS: Emma (female) and Andrew (male) - slow American English podcast

ACTUAL SCRIPT CONTENT (first 15 lines):
{turns_preview}

Create a JSON object with these fields:
1. "titles": Array of 5 viral YouTube title options
2. "selected_title": The BEST title from the array
3. "description": Full YouTube description (500+ words)
4. "tags": Array of 12-15 SEO tags

STRICT RULES - VIOLATION = REJECTION:
- The word "English" MUST appear in every title
- The channel name "English Fluency Studio" MUST appear in the description
- Episode number {ep_num} MUST be mentioned in the description
- The topic "{topic_name}" MUST be referenced in the description
- DO NOT invent fake statistics, viewer counts, or subscriber numbers
- DO NOT claim specific episode counts unless given
- DO NOT add social media handles that don't exist
- Description must accurately reflect the ACTUAL content of this episode
- Use power words: "Secret", "Proven", "Native", "Fluent", "Daily", "Master"
- Include relevant hashtags at the end of description

Return ONLY valid JSON, no markdown."""

    for attempt in range(3):
        try:
            resp = requests.post("https://gen.pollinations.ai/v1/chat/completions", json={
                "model": "gemini-fast",
                "messages": [
                    {"role": "system", "content": "You are a YouTube SEO expert who creates viral titles and descriptions for the English Fluency Studio channel. You NEVER hallucinate statistics or make false claims. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.8
            }, headers=headers, timeout=120)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"].strip()

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            ai_metadata = json.loads(content)

            # Validate: title must contain topic-relevant words
            selected_title = ai_metadata.get("selected_title", "")
            if topic_name.lower() not in selected_title.lower() and keyword.lower() not in selected_title.lower():
                print(f"  ⚠️ Title doesn't match topic, retrying...")
                continue

            # Ensure required fields with fallbacks
            ai_metadata.setdefault("titles", [])
            ai_metadata.setdefault("selected_title", ai_metadata["titles"][0] if ai_metadata["titles"] else f"English Fluency Studio - {topic_name} | Episode {ep_num}")
            ai_metadata.setdefault("description", "")
            ai_metadata.setdefault("tags", ["Learn English", "American English", "English Fluency", "Slow English"])

            # Ensure description mentions channel name
            if "english fluency studio" not in ai_metadata["description"].lower():
                ai_metadata["description"] = f"🎙️ English Fluency Studio Podcast - Episode {ep_num}\n\n" + ai_metadata["description"]

            # Ensure episode number is in description
            if str(ep_num) not in ai_metadata["description"]:
                ai_metadata["description"] = ai_metadata["description"] + f"\n\n📌 Episode: {ep_num}"

            # Add metadata fields
            ai_metadata["topic"] = topic_name
            ai_metadata["keyword"] = keyword
            ai_metadata["episode"] = ep_num
            ai_metadata["duration_seconds"] = duration
            ai_metadata["duration_minutes"] = duration / 60
            ai_metadata["turns_count"] = len(turns)

            print(f"  ✅ AI metadata generated successfully")
            return ai_metadata

        except Exception as e:
            print(f"  ⚠️ AI metadata attempt {attempt+1} failed: {e}")

    # Fallback to basic metadata
    return _fallback_metadata(topic_name, keyword, ep_num, duration, turns)


def _fallback_metadata(topic_name, keyword, ep_num, duration, turns):
    """Fallback metadata when AI fails - always accurate"""
    return {
        "titles": [
            f"Slow American English Podcast - {topic_name} | Episode {ep_num}",
            f"Learn American English - {topic_name} | Speak Fluently",
            f"English Fluency Studio - {topic_name} | Slow & Clear",
            f"Master American English - {topic_name} | Daily Podcast Ep {ep_num}",
        ],
        "selected_title": f"Slow American English Podcast - {topic_name} | Episode {ep_num}",
        "description": f"""🎙️ English Fluency Studio Podcast - Episode {ep_num}

In this episode, we discuss: {topic_name}

This is a slow, clear American English podcast designed for English learners. Two hosts (Emma and Andrew) have a natural conversation at a pace that's easy to follow.

🎯 WHAT YOU'LL LEARN:
• Natural American English expressions
• Slow, clear pronunciation
• Real conversational English
• Everyday vocabulary and phrases

💡 HOW TO USE THIS PODCAST:
1. Listen actively while reading the text on screen
2. Pause and repeat phrases out loud
3. Practice shadowing (speak along with the hosts)
4. Listen multiple times for better retention

🔔 SUBSCRIBE for daily slow English podcasts!
👍 LIKE this video if you found it helpful!
💬 COMMENT which topics you want us to cover next!

#EnglishFluency #LearnEnglish #AmericanEnglish #SlowEnglish #EnglishPodcast #SpeakEnglish #EnglishListening #EnglishPractice #FluencyStudio

---
© English Fluency Studio
""",
        "tags": ["Learn English", "American English", "English Fluency", "Slow English", "English Podcast", "Speak English", "English Listening", "Language Learning"],
        "topic": topic_name,
        "keyword": keyword,
        "episode": ep_num,
        "duration_seconds": duration,
        "duration_minutes": duration / 60,
        "turns_count": len(turns)
    }

if __name__ == "__main__":
    turns_cnt = 5 if len(sys.argv) > 1 and sys.argv[1] == "--test" else 360
    asyncio.run(run_full_generator(topic_index=0, custom_turns=turns_cnt))
