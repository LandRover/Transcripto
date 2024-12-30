import re
import logging
import requests
from .download_base import DownloadBase
from .url_download import URLDownload
from transcripto.utils.http import is_valid_url
from transcripto.services.podcast_providers.pocketcasts.pocketcasts_api import PocketCastsAPI
from pathlib import Path

class PocketCastsDownload(DownloadBase):
    provider = {}


    def __init__(self):
        self.provider = PocketCastsAPI()


    def get_episode_id(self, url):
        url_parts = self.provider.extract_media_from_url(url)

        return url_parts.id
    

    def download(self, url: str, temp_path: Path):
        logging.info(f"PocketCastsDownload starting download {url}...")

        try:
            episode_metadata = self.provider.get_episode_metadata(url)
            episode_audio_url = episode_metadata.episode_audio_url
            
            url_downloader = URLDownload()
            
            if is_valid_url(episode_audio_url):
                logging.info(f"Detected a url for a podcast episode {episode_audio_url}, Offloading to URLDownload")
                mp3_content = url_downloader.download(episode_audio_url, temp_path)
                return mp3_content
            else:
                logging.error(f"MP3 path could not be deleted from this podcast: {url}")
                return None
        
        except requests.RequestException as e:
            logging.error(f"Failed to download file: {e}")
            raise
