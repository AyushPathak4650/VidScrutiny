import os
import yt_dlp
import uuid

def download_audio(url: str) -> str:
    """
    Downloads the audio track from a given video URL securely.
    Returns the absolute path to the downloaded audio file.
    """
    # Create an absolute path for the temp directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    temp_dir = os.path.join(base_dir, "temp_files")
    
    # Generate a unique filename to prevent collisions
    unique_id = str(uuid.uuid4())
    output_template = os.path.join(temp_dir, f"{unique_id}.%(ext)s")
    
    ydl_opts = {
        # Limit video resolution to 480p to drastically reduce file size and download time.
        # Whisper only cares about the audio, and 480p is perfectly fine for a web UI demo.
        'format': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4][height<=480]/best',
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        
        # Concurrent downloading to bypass throttling
        'concurrent_fragment_downloads': 10,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info to get the exact final filename
            info_dict = ydl.extract_info(url, download=True)
            ext = info_dict.get('ext', 'mp4')
            final_filename = os.path.join(temp_dir, f"{unique_id}.{ext}")
            return final_filename
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "Sign in to confirm you’re not a bot" in error_msg:
            raise Exception("YouTube's anti-bot system blocked our cloud server (Render). For this live demo, please paste a direct .mp4 link or a video from a platform with looser restrictions!")
        if "403: Forbidden" in error_msg:
            raise Exception("The server hosting this video blocked our download request (HTTP 403). Please try a different URL, like the default Archive.org video provided.")
        raise Exception(f"Failed to download video: {error_msg}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred during audio extraction: {str(e)}")

def cleanup_file(filepath: str):
    """Safely deletes the temporary file."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Error cleaning up file {filepath}: {e}")
