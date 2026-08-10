"""
SLOW ENGLISH PODCAST - MASTER RUNNER
Easy command line runner for generating 30-minute podcasts, thumbnails, and custom scripts.
"""
import os, sys, asyncio
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR))

from podcast_generator import run_full_generator, TOPICS
from thumbnail_generator import create_thumbnail

def print_banner():
    print("=" * 70)
    print("      🎙️  SLOW ENGLISH PODCAST AUTOMATION BOT  🎙️")
    print("   Generates 30-Min Slow English Videos & High-CTR Thumbnails")
    print("=" * 70)

def main():
    print_banner()
    print("\nSelect an action:")
    print("  1. Generate Full 30-Minute Slow English Video & Thumbnail")
    print("  2. Quick Test Run (2-Minute Video)")
    print("  3. Generate High-Converting YouTube Thumbnail Only")
    print("  4. View Available Topics")
    print("  5. Exit")

    choice = input("\nEnter choice (1-5): ").strip()

    if choice == "1":
        print("\nSelect Topic:")
        for idx, t in enumerate(TOPICS):
            print(f"  {idx + 1}. {t['topic']}")
        t_choice = input(f"\nSelect topic (1-{len(TOPICS)}, default 1): ").strip()
        t_idx = int(t_choice) - 1 if t_choice.isdigit() and 1 <= int(t_choice) <= len(TOPICS) else 0
        
        asyncio.run(run_full_generator(topic_index=t_idx, custom_turns=120))

    elif choice == "2":
        asyncio.run(run_full_generator(topic_index=0, custom_turns=5))

    elif choice == "3":
        title = input("Enter thumbnail main title (e.g. HOW TO THINK IN ENGLISH): ").strip() or "HOW TO THINK IN ENGLISH"
        highlight = input("Enter word to highlight in yellow (e.g. THINK): ").strip() or "THINK"
        sub = input("Enter subtitle pill text (e.g. SLOW ENGLISH FOR BEGINNERS): ").strip() or "SLOW ENGLISH FOR BEGINNERS"
        ep = input("Enter episode number (e.g. 1): ").strip()
        ep_num = int(ep) if ep.isdigit() else 1
        
        create_thumbnail(title, highlight, sub, ep_num, f"custom_thumbnail_ep{ep_num}.png")

    elif choice == "4":
        print("\n--- Available Topics ---")
        for idx, t in enumerate(TOPICS):
            print(f" [{idx+1}] Topic: {t['topic']}")
            print(f"     Keyword: {t['keyword']} | Subtitle: {t['sub']}\n")

    else:
        print("Exiting.")

if __name__ == "__main__":
    main()
