import re
import logging
import requests
import urllib.parse
from .download_base import DownloadBase
from .url_download import URLDownload
from transcripto.utils.file_utils import extract_filename_from_url
from pathlib import Path

class ApplePodcastDownload(DownloadBase):
    def get_episode_id(self, url):

        # Parse the query parameters
        query = urllib.parse.urlparse(url).query
        params = urllib.parse.parse_qs(query)

        # Extract the value of 'i'
        return params.get('i', [None])[0]


    def download(self, url: str, temp_path: Path):
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
                mp3_content = url_downloader.download(mp3_path, temp_path)
                return mp3_content
            else:
                logging.error(f"MP3 path could not be deleted from this podcast: {url}")
                return None
        
        except requests.RequestException as e:
            logging.error(f"Failed to download file: {e}")
            raise
