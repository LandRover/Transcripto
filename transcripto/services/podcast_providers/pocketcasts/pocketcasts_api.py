import logging
import requests
from transcripto.utils.file import extract_filename_from_url
from transcripto.utils.http import verify_response
from transcripto.utils.json import match_patterns
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

            extractor_patterns = [
                {"key": "show_title", "pattern": r'<meta property="og:title" content="(.*?)">'},
                {"key": "show_description", "pattern": r'<meta property="og:description" content="(.*?)">'},
                {"key": "show_date", "pattern": r'<div id="episode_date">(.*?)</div>'},
                {"key": "show_notes", "pattern": r'<div class="section show_notes">(.*?)</div>'},
                {"key": "audio_url", "pattern": r'<audio[^>]*\s+src="([^"]+\.mp3[^"]*)"'},
            ]

            extracted_data = match_patterns(html_response.text, extractor_patterns)

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
