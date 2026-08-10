"""
YouTube Long-Form Video Upload Script - English Fluency Studio
Uploads 30-minute podcast video with title, description, tags, and thumbnail
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# YouTube API credentials
YT_CLIENT_ID = os.getenv("YT_CLIENT_ID")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET")
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN")


def get_latest_podcast():
    """Find the most recently generated podcast video"""
    base_dir = Path(__file__).parent.parent
    output_dir = base_dir / "output"

    if not output_dir.exists():
        print("❌ No output directory found")
        return None

    # Get latest run directory
    dirs = sorted([d for d in output_dir.iterdir() if d.is_dir() and d.name.startswith("run_")],
                  key=lambda x: x.stat().st_mtime, reverse=True)

    if not dirs:
        print("❌ No podcast run directories found")
        return None

    latest_dir = dirs[0]
    print(f"📁 Found latest podcast: {latest_dir.name}")

    # Check for required files
    video_file = latest_dir / "podcast_30min_final.mp4"
    metadata_file = latest_dir / "youtube_metadata.json"
    thumbnail_files = list(latest_dir.glob("thumbnail_*.png"))

    if not video_file.exists():
        print(f"❌ Video file not found: {video_file}")
        return None

    thumbnail_file = thumbnail_files[0] if thumbnail_files else None
    if thumbnail_file:
        print(f"🖼️  Found thumbnail: {thumbnail_file.name}")
    else:
        print("⚠️  No thumbnail found")

    return {
        "dir": latest_dir,
        "video": video_file,
        "thumbnail": thumbnail_file,
        "metadata": metadata_file if metadata_file.exists() else None
    }


def upload_to_youtube(podcast_info):
    """Upload video to YouTube using Google API"""
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from googleapiclient.errors import HttpError
    except ImportError:
        print("❌ YouTube API libraries not installed.")
        print("   Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return False

    SCOPES = [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube"
    ]
    API_SERVICE_NAME = "youtube"
    API_VERSION = "v3"

    # Try to use refresh token first
    if YT_REFRESH_TOKEN:
        print("🔑 Using refresh token for authentication...")
        try:
            credentials = Credentials(
                None,
                refresh_token=YT_REFRESH_TOKEN,
                client_id=YT_CLIENT_ID,
                client_secret=YT_CLIENT_SECRET,
                token_uri="https://oauth2.googleapis.com/token"
            )
            credentials.refresh(Request())
            print("✅ Authentication successful!")
        except Exception as e:
            print(f"⚠️  Refresh token failed: {e}")
            credentials = None
    else:
        credentials = None

    if not credentials:
        print("❌ No valid YouTube credentials found.")
        print("   Please set YT_REFRESH_TOKEN in your .env or secrets")
        return False

    # Build YouTube API client
    youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    youtube._http.timeout = 600

    # Get title and description from metadata
    title = "English Fluency Studio - Slow American English Podcast"
    description = ""
    tags = []

    if podcast_info.get("metadata") and podcast_info["metadata"].exists():
        with open(podcast_info["metadata"], "r", encoding="utf-8") as f:
            metadata = json.load(f)
            title = metadata.get("selected_title", title)
            description = metadata.get("description", description)
            tags = metadata.get("tags", tags)

    # Truncate description if too long (YouTube limit: 5000 characters)
    if len(description) > 4800:
        description = description[:4800] + "\n\n... (truncated)"

    print(f"\n📹 Uploading podcast to YouTube...")
    print(f"   Title: {title[:80]}...")

    # Prepare video metadata
    video_metadata = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags if tags else [
                "Learn English",
                "American English",
                "English Fluency",
                "Slow English",
                "English Podcast",
                "Speak English",
                "English Listening",
                "Language Learning"
            ],
            "categoryId": "27"  # Education
        },
        "status": {
            "privacyStatus": "public",  # Upload as public immediately
            "selfDeclaredMadeForKids": False
        }
    }

    # Upload video
    try:
        media = MediaFileUpload(str(podcast_info["video"]), chunksize=1024*1024*10, resumable=True)

        request = youtube.videos().insert(
            part=",".join(video_metadata.keys()),
            body=video_metadata,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"   Upload progress: {progress}%")

        video_id = response["id"]
        print(f"\n✅ Video uploaded successfully!")
        print(f"   Video ID: {video_id}")
        print(f"   URL: https://www.youtube.com/watch?v={video_id}")
        print(f"   Status: Public (visible to everyone)")

        # Upload thumbnail
        if podcast_info.get("thumbnail") and podcast_info["thumbnail"].exists():
            print(f"\n🖼️  Uploading custom thumbnail...")
            try:
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(str(podcast_info["thumbnail"]))
                ).execute()
                print(f"   ✅ Thumbnail uploaded successfully!")
            except HttpError as e:
                print(f"   ⚠️  Thumbnail upload failed: {e}")
                print(f"   You can manually upload thumbnail from the podcast directory")

        # Save upload result
        result_file = podcast_info["dir"] / "youtube_upload_result.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump({
                "video_id": video_id,
                "title": title,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "status": "public",
                "uploaded_at": str(Path(podcast_info["dir"]).stat().st_mtime)
            }, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Upload result saved to: {result_file}")

        return True

    except HttpError as e:
        print(f"\n❌ YouTube upload failed: {e}")
        if "quotaExceeded" in str(e):
            print("   ⚠️  Daily upload quota exceeded. Try again tomorrow.")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


def main():
    print("\n" + "="*80)
    print("🎙️  ENGLISH FLUENCY STUDIO - YOUTUBE PODCAST UPLOADER")
    print("="*80)

    # Find latest podcast
    podcast_info = get_latest_podcast()
    if not podcast_info:
        print("\n❌ No podcast found to upload")
        print("   Run podcast_generator.py first to generate a podcast")
        return False

    print(f"\n📁 Podcast Directory: {podcast_info['dir']}")
    print(f"   🎬 Video: {podcast_info['video'].name}")
    print(f"   🖼️  Thumbnail: {podcast_info['thumbnail'].name if podcast_info.get('thumbnail') else 'Not found'}")

    # Confirm upload
    print(f"\n✅ Podcast will be uploaded as PUBLIC")
    print(f"   It will be visible to everyone immediately")

    # Check if running in GitHub Actions (non-interactive)
    if os.getenv("GITHUB_ACTIONS") == "true":
        print(f"\n🤖 Running in GitHub Actions - auto-confirming upload")
        confirm = True
    else:
        response = input(f"\nProceed with upload? (yes/no): ").strip().lower()
        confirm = response in ["yes", "y"]

    if not confirm:
        print("❌ Upload cancelled")
        return False

    # Upload to YouTube
    success = upload_to_youtube(podcast_info)

    print("\n" + "="*80)
    if success:
        print("✅ UPLOAD COMPLETE!")
        print("   Check your YouTube Studio for the uploaded podcast")
    else:
        print("❌ UPLOAD FAILED")
        print("   Check the error messages above")
        print("   You can manually upload the podcast files from:")
        print(f"   {podcast_info['dir']}")
    print("="*80 + "\n")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
