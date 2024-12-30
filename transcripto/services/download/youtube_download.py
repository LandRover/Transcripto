import logging
import io
import re
import os
import yt_dlp
from .download_base import DownloadBase
from pathlib import Path

class YoutubeDownload(DownloadBase):
    def get_episode_id(self, url):
        youtube_regex = r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:[&?\/]|$)'
        match = re.search(youtube_regex, url)

        return match.group(1) if match else None


    def download(self, url: str, temp_path: Path):
        output_directory = temp_path
        output_filename_format = '%(id)s - %(title)s (%(uploader)s) (%(id)s) (%(upload_date)s).%(ext)s'

        try:
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
                info_dict = ydl.extract_info(url, download=True)
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

