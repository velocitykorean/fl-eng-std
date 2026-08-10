import os, subprocess, win32com.client
from pathlib import Path

OUT_DIR = Path(__file__).parent / "output_test"
OUT_DIR.mkdir(parents=True, exist_ok=True)

speaker = win32com.client.Dispatch("SAPI.SpVoice")
voices = speaker.GetVoices()

# Map voices by name
zira_voice = None
david_voice = None
for i in range(voices.Count):
    v = voices.Item(i)
    desc = v.GetDescription()
    if "Zira" in desc:
        zira_voice = v
    elif "David" in desc:
        david_voice = v

print("Found Zira:", zira_voice.GetDescription() if zira_voice else "None")
print("Found David:", david_voice.GetDescription() if david_voice else "None")

def text_to_wav(text, voice_obj, output_wav_path, rate_speed=-2):
    """
    Saves TTS text to WAV using SAPI.SpVoice with custom speech rate.
    rate_speed: -2 or -3 for slow, deliberate American English pace!
    """
    stream = win32com.client.Dispatch("SAPI.SpFileStream")
    from win32com.client import constants
    # SpeechAudioFormatType SAFT44kHz16BitStereo = 39 or SAFT22kHz16BitMono
    stream.Open(str(output_wav_path), 3, False) # 3 = SSFMCreateForWrite
    
    speaker.Voice = voice_obj
    speaker.Rate = rate_speed  # Slow American English rate!
    speaker.AudioOutputStream = stream
    speaker.Speak(text)
    stream.Close()
    
    # Convert WAV to MP3 using FFmpeg
    mp3_path = Path(output_wav_path).with_suffix(".mp3")
    subprocess.run(["ffmpeg", "-y", "-i", str(output_wav_path), "-b:a", "192k", str(mp3_path)], capture_output=True, check=True)
    Path(output_wav_path).unlink(missing_ok=True)
    return mp3_path

wav1 = OUT_DIR / "test_zira_american.wav"
wav2 = OUT_DIR / "test_david_american.wav"

mp3_zira = text_to_wav("Welcome to Slow American English Podcast. My name is Emma.", zira_voice, wav1, rate_speed=-2)
mp3_david = text_to_wav("And I am Andrew. We speak clear, slow American English.", david_voice, wav2, rate_speed=-2)

print("Generated Zira (American Female):", mp3_zira, "Size:", mp3_zira.stat().st_size)
print("Generated David (American Male):", mp3_david, "Size:", mp3_david.stat().st_size)
