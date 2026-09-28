"""
Facebook Page Video Upload Script for English Fluency Studio
Uses Facebook Graph API to upload podcast and fluency lesson videos to the English Fluency Studio Facebook Page.
Supports chunked resumable upload for large video files.
"""
import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

GRAPH_API_VERSION = "v20.0"


def get_facebook_credentials():
    """Retrieve Facebook Page ID and Page Access Token from environment."""
    page_id = (
        os.getenv('FB_PAGE_ID') or
        os.getenv('FACEBOOK_PAGE_ID') or
        os.getenv('ENGLISH_FLUENCY_STUDIO_FB_PAGE_ID', '1339196409275108')
    ).strip()

    access_token = (
        os.getenv('FB_PAGE_ACCESS_TOKEN') or
        os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN') or
        os.getenv('ENGLISH_FLUENCY_STUDIO_FB_PAGE_ACCESS_TOKEN', '')
    ).strip()

    def mask(s):
        return f"{s[:4]}...{s[-4:]}" if s and len(s) > 8 else ("PRESENT" if s else "MISSING")

    print(f"[facebook] Page ID: {mask(page_id)}")
    print(f"[facebook] Access Token: {'PRESENT (len=' + str(len(access_token)) + ')' if access_token else 'MISSING'}")

    if not page_id or not access_token:
        raise ValueError(
            "Missing Facebook credentials! Set these environment variables or GitHub Secrets:\n"
            "  - FB_PAGE_ID\n"
            "  - FB_PAGE_ACCESS_TOKEN"
        )

    return page_id, access_token


def upload_video_resumable(video_path, title, description, page_id, access_token):
    """
    Upload video using Meta Graph API chunked resumable upload protocol.
    Recommended for reliable uploads of video files of any size.
    """
    file_size = os.path.getsize(video_path)
    print(f"[facebook] Starting resumable upload for '{title}' ({file_size / (1024 * 1024):.2f} MB)...")

    # Phase 1: START
    start_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{page_id}/videos"
    start_payload = {
        "upload_phase": "start",
        "file_size": file_size,
        "access_token": access_token
    }
    resp = requests.post(start_url, data=start_payload)
    if resp.status_code != 200:
        raise RuntimeError(f"Resumable upload START failed ({resp.status_code}): {resp.text}")

    start_data = resp.json()
    upload_session_id = start_data["upload_session_id"]
    video_id = start_data.get("video_id")
    start_offset = int(start_data.get("start_offset", 0))
    end_offset = int(start_data.get("end_offset", 0))

    # Phase 2: TRANSFER CHUNKS
    chunk_size = end_offset - start_offset if end_offset > start_offset else (4 * 1024 * 1024)
    with open(video_path, "rb") as f:
        while start_offset < file_size:
            f.seek(start_offset)
            chunk_data = f.read(chunk_size)
            if not chunk_data:
                break

            transfer_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{page_id}/videos"
            transfer_data = {
                "upload_phase": "transfer",
                "upload_session_id": upload_session_id,
                "start_offset": start_offset,
                "access_token": access_token
            }
            transfer_files = {
                "video_file_chunk": ("chunk.mp4", chunk_data, "video/mp4")
            }

            t_resp = requests.post(transfer_url, data=transfer_data, files=transfer_files)
            if t_resp.status_code != 200:
                raise RuntimeError(f"Resumable upload TRANSFER failed at offset {start_offset} ({t_resp.status_code}): {t_resp.text}")

            t_data = t_resp.json()
            new_start = int(t_data.get("start_offset", start_offset + len(chunk_data)))
            new_end = int(t_data.get("end_offset", new_start + chunk_size))
            chunk_size = new_end - new_start if new_end > new_start else chunk_size

            pct = min(100, int((new_start / file_size) * 100))
            print(f"[facebook] Upload progress: {pct}%")
            start_offset = new_start

    # Phase 3: FINISH
    print("[facebook] Finalizing video processing with title & description...")
    finish_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{page_id}/videos"
    finish_payload = {
        "upload_phase": "finish",
        "upload_session_id": upload_session_id,
        "title": title,
        "description": description,
        "access_token": access_token
    }
    f_resp = requests.post(finish_url, data=finish_payload)
    if f_resp.status_code != 200:
        raise RuntimeError(f"Resumable upload FINISH failed ({f_resp.status_code}): {f_resp.text}")

    result = f_resp.json()
    final_video_id = result.get("id") or video_id
    print(f"[facebook] Video uploaded successfully! Video ID: {final_video_id}")
    print(f"[facebook] Watch URL: https://www.facebook.com/{page_id}/videos/{final_video_id}")
    return {"id": final_video_id, "success": True, "data": result}


def upload_video_direct(video_path, title, description, page_id, access_token):
    """Fallback single-request multipart upload for standard video files."""
    print(f"[facebook] Direct uploading: {title}")
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{page_id}/videos"
    payload = {
        "title": title,
        "description": description,
        "access_token": access_token
    }
    with open(video_path, "rb") as f:
        files = {"source": (os.path.basename(video_path), f, "video/mp4")}
        resp = requests.post(url, data=payload, files=files, timeout=600)

    if resp.status_code != 200:
        raise RuntimeError(f"Direct video upload failed ({resp.status_code}): {resp.text}")

    data = resp.json()
    video_id = data.get("id")
    print(f"[facebook] Uploaded! Video ID: {video_id}")
    print(f"[facebook] URL: https://www.facebook.com/{page_id}/videos/{video_id}")
    return data


def upload_to_facebook(video_path, title, description):
    """
    Upload a video to the configured Facebook Page.
    Attempts resumable upload first, with automatic fallback to direct multipart upload.
    """
    page_id, access_token = get_facebook_credentials()

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    try:
        return upload_video_resumable(video_path, title, description, page_id, access_token)
    except Exception as e:
        print(f"[facebook] Resumable upload encountered issue ({e}), falling back to direct upload...")
        return upload_video_direct(video_path, title, description, page_id, access_token)


def main():
    if len(sys.argv) < 2:
        print("Usage: python publish_facebook.py <video_path> [title|metadata_json] [description]")
        sys.exit(1)

    video_path = sys.argv[1]
    title = "English Fluency Studio - Slow English Podcast"
    description = (
        "Improve your English fluency and listening comprehension with English Fluency Studio. "
        "Learn natural expressions, clear pronunciation, and conversational confidence. 🎙️📚🌟"
    )

    # Check if second arg is metadata JSON
    if len(sys.argv) > 2:
        arg2 = sys.argv[2]
        if arg2.endswith(".json") and os.path.exists(arg2):
            try:
                with open(arg2, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    title = meta.get("selected_title") or meta.get("title") or title
                    description = meta.get("description") or description
            except Exception as e:
                print(f"[facebook] Warning reading metadata JSON: {e}")
        else:
            title = arg2
            if len(sys.argv) > 3:
                description = sys.argv[3]

    try:
        result = upload_to_facebook(video_path, title, description)
        fb_id = result.get("id")

        # Save result JSON in same dir as video if possible
        video_dir = Path(video_path).parent
        if video_dir.exists():
            out_file = video_dir / "facebook_upload_result.json"
            page_id, _ = get_facebook_credentials()
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump({
                    "video_id": fb_id,
                    "title": title,
                    "url": f"https://www.facebook.com/{page_id}/videos/{fb_id}",
                    "status": "published"
                }, f, indent=2, ensure_ascii=False)
            print(f"[facebook] Saved upload record to: {out_file}")

    except Exception as exc:
        print(f"[facebook] Upload failed: {exc}")
        sys.exit(1)


if __name__ == '__main__':
    main()
