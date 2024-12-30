import logging
import io
import re
import os
import yt_dlp
from .download_base import DownloadBase
from transcripto.services.podcast_providers.youtube.youtube_api import YoutubeAPI
from pathlib import Path

class YoutubeDownload(DownloadBase):
    provider = {}


    def __init__(self):
        self.provider = YoutubeAPI()


    def get_episode_id(self, url):
        url_parts = self.provider.extract_media_from_url(url)

        return url_parts.id


    def download(self, url: str, temp_path: Path):
        output_directory = temp_path
        output_filename_format = '%(id)s - %(title)s (%(uploader)s) (%(id)s) (%(upload_date)s).%(ext)s'

        try:
            episode_metadata = self.provider.get_episode_metadata(url)
            episode_audio_url = episode_metadata.episode_audio_url

            # Create an in-memory buffer
            buffer = io.BytesIO()

            # Configure yt_dlp options
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(output_directory, output_filename_format),
                'quiet': True,  # Suppress yt_dlp logs
            }

            # Download audio
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(episode_audio_url, download=True)
                file_path = ydl.prepare_filename(info_dict)
                file_path = os.path.splitext(file_path)[0] + ".mp3"  # Adjust for postprocessor

            logging.info("Download and conversion completed successfully.")

            # Read the file into the buffer
            with open(file_path, 'rb') as f:
                buffer.write(f.read())

            # Delete the temporary file
            os.remove(file_path)

            buffer.seek(0)  # Reset buffer pointer
            mp3_bytes = buffer.read()  # Return the binary MP3 content
            
            return mp3_bytes

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return None

