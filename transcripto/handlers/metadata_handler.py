import logging
from mutagen.mp3 import MP3

def fetch_audio_metadata(filepath):
    """
    Fetch metadata from an MP3 file.

    Args:
        filepath (str): Path to the MP3 file.

    Returns:
        dict: A dictionary containing metadata such as duration, bitrate, and channels.
    """
    try:
        audio = MP3(filepath)
        metadata = {
            "duration": audio.info.length,  # Duration in seconds
            "bitrate": audio.info.bitrate,  # Bitrate in kbps
            "channels": audio.info.channels,  # Number of audio channels
        }
        
        return metadata
    except Exception as e:
        logging.error(f"Failed to extract metadata from {filepath}: {e}")
        return {}
