import re
import logging
import requests
from transcripto.utils.http import verify_response
from transcripto.utils.json import match_patterns
from .models import YoutubeURL, YoutubeDownloadItem

class YoutubeAPI:
    YOUTUBE_HOME_PAGE_URL = "https://www.youtube.com"


    def __init__(self):
        self.__apply_requests_session()


    def __apply_requests_session(self):
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "text/html",
            "accept-language": "en-US",
            "content-type": "text/html",
            "origin": self.YOUTUBE_HOME_PAGE_URL,
            "referer": self.YOUTUBE_HOME_PAGE_URL,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/131.0.0.0 Safari/537.36",
        })


    def get_episode_metadata(self, url: str) -> list[YoutubeDownloadItem]:
        try:
            html_response = requests.get(url, stream=True)
            verify_response(html_response)

            extractor_patterns = [
                {"key": "ytInitialPlayerResponse", "pattern": r'<script nonce="[^"]+">var ytInitialPlayerResponse = ({.*?});<\/script>'},
            ]

            extracted_data = match_patterns(html_response.text, extractor_patterns)

        except requests.RequestException as e:
            logging.error(f"Failed to fetch episode data: {e}")
            raise
        
        return YoutubeDownloadItem(
            episode_info = extracted_data["ytInitialPlayerResponse"]["videoDetails"],
            episode_audio_url = url,
        )


    def extract_media_from_url(self, url) -> list[YoutubeURL]:
        youtube_regex = r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:[&?\/]|$)'
        match = re.search(youtube_regex, url)

        return YoutubeURL(
            id = match.group(1) if match else None,
        )
