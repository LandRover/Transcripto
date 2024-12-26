import re
import logging
import requests
from .download_base import DownloadBase
from .url_download import URLDownload
from transcripto.utils.file_utils import extract_filename_from_url
from pathlib import Path

class ApplePodcastDownload(DownloadBase):
    def get_filename(self, url):
        filename = extract_filename_from_url(url)
        
        return filename
    
    def download(self, url):
        logging.info(f"ApplePodcastDownload starting download {url}...")

        try:
            response = requests.get(url, stream = True)
            response.raise_for_status()
            
            # Extract the streamUrl using a regex pattern
            stream_url_pattern = r'"streamUrl":"(https?://[^"]+\.mp3)"'
            match = re.search(stream_url_pattern, response.text)
            url_downloader = URLDownload()
            
            if match:
                mp3_path = match.group(1)
                logging.info(f"Detected a url for a podcast episode {mp3_path}, Offloading to URLDownload")
                mp3_content = url_downloader.download(mp3_path)
                return mp3_content
            else:
                logging.error(f"MP3 path could not be deleted from this podcast: {url}")
                return None
        
        except requests.RequestException as e:
            logging.error(f"Failed to download file: {e}")
            raise
