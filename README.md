# 🎙️ Slow English Podcast Automation Bot

An automated broadcast generator for **30-Minute Slow English Podcasts** designed specifically for YouTube channels. The bot creates high-definition (1920x1080) video broadcasts and high-CTR YouTube thumbnails matching the exact design aesthetic provided in reference assets.

---

## 📸 Key Design Features
- **Host & Studio Layout**: Features the host woman with her microphone integrated on the left side of a dark studio setting.
- **Dynamic Word Highlighting**: Renders spoken sentences in clean white sans-serif typography with key vocabulary highlighted in **vibrant yellow (`#FFD700`)**.
- **Signature Subtitle Line**: `"Learn English • Think Better • Speak Confidently"`.
- **Audio & Pace**: Slow, clear, deliberate English pace (`-15%` rate) using ultra-realistic Microsoft Edge Neural TTS voices (`en-US-AvaNeural` for Emma & `en-US-AndrewNeural` for Andrew).
- **YouTube Thumbnails**: Automated thumbnail creation with eye-catching yellow headline badges and episode pills.

---

## 📁 File Structure
```
Slow English podcast/
├── assets/
│   ├── woman_base.png          # Studio background with host on left
│   ├── background.png          # Studio background image
│   ├── layer_woman.png         # Standalone cutout layer of host
│   └── style_reference.png     # Reference style sample
├── output/                     # Generated videos & thumbnails
├── podcast_generator.py        # Main video broadcast & audio generator
├── thumbnail_generator.py      # Automated YouTube thumbnail generator
├── run_generator.py            # Master CLI runner
└── README.md                   # System documentation
```

---

## 🚀 How to Run

### 1. Interactive Master Runner
Run the interactive menu to select topics, run quick tests, or generate custom thumbnails:
```bash
python run_generator.py
```

### 2. Generate Full 30-Minute Podcast Video
To generate a complete ~30-minute podcast video and matching thumbnail:
```bash
python podcast_generator.py
```

### 3. Quick 2-Minute Test Run
To test script generation, TTS audio, and video rendering:
```bash
python podcast_generator.py --test
```

### 4. Generate Thumbnail Only
To generate custom high-converting YouTube thumbnails:
```bash
python thumbnail_generator.py
```

---

## 🎯 Included Topics
1. *How to Think Directly in English Without Translating*
2. *Building Confidence to Speak English Everyday*
3. *The Power of Daily English Listening Habits*
4. *Overcoming the Fear of Making Mistakes in English*
5. *How to Learn English Vocabulary Naturally*
6. *Small Talk and Everyday Conversations in English*
7. *Mastering English Pronunciation and Rhythm*
8. *Traveling and Exploring New Cultures in English*
9. *Work, Career, and Professional English Basics*
10. *The Secret to Fluency: Consistency Over Perfection*
