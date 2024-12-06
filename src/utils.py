import os
from mutagen.mp3 import MP3
import logging
from urllib.parse import urlparse


def validate_audio_file(filepath):
    parsed = urlparse(filepath)
    if parsed.scheme in ["http", "https"]:
        # URL detected, skip local file checks
        return
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    if not filepath.lower().endswith(".mp3"):
        raise ValueError(f"Invalid file format. Expected .mp3, got: {filepath}")

def cleanup_temp_files(temp_dir):
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    logging.info("Temporary files cleaned up.")


def extract_audio_metadata(filepath):
    audio = MP3(filepath)
    return {
        "duration": audio.info.length,
        "bitrate": audio.info.bitrate,
        "channels": audio.info.channels
    }
