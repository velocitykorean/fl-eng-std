import os, asyncio
from pathlib import Path
from gtts import gTTS

OUT_DIR = Path(__file__).parent / "output_test"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Test 1: gTTS
print("Testing gTTS...")
try:
    tts = gTTS(text="Welcome to the Slow English Podcast. Learn English step by step with clear audio.", lang='en', slow=True)
    out1 = OUT_DIR / "test_gtts.mp3"
    tts.save(str(out1))
    print(f"gTTS audio generated successfully: {out1} (Size: {out1.stat().st_size} bytes)")
except Exception as e:
    print(f"gTTS error: {e}")

# Test 2: edge-tts
async def test_edge():
    import edge_tts
    print("Testing edge-tts...")
    try:
        communicate = edge_tts.Communicate("Welcome to the Slow English Podcast. Learn English step by step with clear audio.", "en-US-AvaNeural", rate="-15%")
        out2 = OUT_DIR / "test_edge.mp3"
        await communicate.save(str(out2))
        print(f"edge-tts audio generated successfully: {out2} (Size: {out2.stat().st_size} bytes)")
    except Exception as e:
        print(f"edge-tts error: {e}")

asyncio.run(test_edge())
