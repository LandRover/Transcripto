import re
import logging
import requests
from .download_base import DownloadBase
from .url_download import URLDownload
from transcripto.services.podcast_providers.apple_podcasts.apple_podcasts_api import ApplePodcastsAPI
from transcripto.utils.http import is_valid_url
from pathlib import Path

class ApplePodcastDownload(DownloadBase):
    provider = {}
    url_downloader = {}

    def __init__(self):
        self.provider = ApplePodcastsAPI()
        self.url_downloader = URLDownload()


    def get_episode_id(self, url):
        url_parts = self.provider.extract_media_from_url(url)

        return url_parts.episode_id


    def download(self, url: str, temp_path: Path):
        logging.info(f"ApplePodcastDownload starting download {url}...")

        try:
            episode_metadata = self.provider.get_episode_metadata(url)
            episode_audio_url = episode_metadata.episode_audio_url
        
            if is_valid_url(episode_audio_url):
                logging.info(f"Detected a url for a podcast episode {episode_audio_url}, Offloading to URLDownload")
                mp3_content = self.url_downloader.download(episode_audio_url, temp_path)
                return mp3_content
            else:
                logging.error(f"Episode failed to detect a valid url: {episode_audio_url} from this podcast: {url}")
                return None
        
        except requests.RequestException as e:
            logging.error(f"Failed to download file: {e}")
            raise
