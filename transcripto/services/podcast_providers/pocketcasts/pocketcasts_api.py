import re
import logging
import json
import requests
from transcripto.utils.file_utils import extract_filename_from_url
from transcripto.utils.http import verify_response
from .models import PocketCastsURL, PocketCastsDownloadItem

class PocketCastsAPI:
    POCKETCASTS_HOME_PAGE_URL = "https://pocketcasts.com"


    def __init__(self):
        self.__apply_requests_session()


    def __apply_requests_session(self):
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "text/html",
            "accept-language": "en-US",
            "content-type": "text/html",
            "origin": self.POCKETCASTS_HOME_PAGE_URL,
            "referer": self.POCKETCASTS_HOME_PAGE_URL,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/131.0.0.0 Safari/537.36",
        })


    def get_episode_metadata(self, url: str) -> list[PocketCastsDownloadItem]:
        try:
            html_response = requests.get(url, stream=True)
            verify_response(html_response)

            html = html_response.text

            patterns = [
                {"key": "audio_url", "pattern": r'<audio[^>]*\s+src="([^"]+\.mp3[^"]*)"'},
            ]

            extracted_data = {}
            for item in patterns:
                match = re.search(item["pattern"], html, re.DOTALL)
                if match:
                    match_str = match.group(1).strip()
                    try:
                        extracted_data[item["key"]] = json.loads(match_str)
                    except json.JSONDecodeError as e:
                        extracted_data[item["key"]] = match_str

        except requests.RequestException as e:
            logging.error(f"Failed to fetch episode data: {e}")
            raise
        
        return PocketCastsDownloadItem(
            episode_info = None,
            episode_audio_url = extracted_data["audio_url"],
        )


    def extract_media_from_url(self, url) -> list[PocketCastsURL]:
        filename = extract_filename_from_url(url)
        
        return PocketCastsURL(
            id = filename,
        )
