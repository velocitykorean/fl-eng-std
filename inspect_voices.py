import os, asyncio, win32com.client

print("=== 1. Inspecting Windows SAPI5 Voices ===")
speaker = win32com.client.Dispatch("SAPI.SpVoice")
voices = speaker.GetVoices()
print(f"Total SAPI5 voices installed: {voices.Count}")
for i in range(voices.Count):
    v = voices.Item(i)
    print(f"  Voice {i}: {v.GetDescription()}")

print("\n=== 2. Testing edge-tts American Neural Voices ===")
async def test_edge():
    import edge_tts
    # Test Female American Voice
    try:
        c1 = edge_tts.Communicate("Hello! I am Emma, speaking in slow American English.", "en-US-AvaNeural", rate="-15%")
        await c1.save("test_emma_american.mp3")
        print("  - Emma (en-US-AvaNeural) SUCCESS! Size:", os.path.getsize("test_emma_american.mp3"))
    except Exception as e:
        print("  - Emma edge-tts failed:", e)

    # Test Male American Voice
    try:
        c2 = edge_tts.Communicate("Hello! I am Andrew, speaking in slow American English.", "en-US-AndrewNeural", rate="-15%")
        await c2.save("test_andrew_american.mp3")
        print("  - Andrew (en-US-AndrewNeural) SUCCESS! Size:", os.path.getsize("test_andrew_american.mp3"))
    except Exception as e:
        print("  - Andrew edge-tts failed:", e)

asyncio.run(test_edge())
