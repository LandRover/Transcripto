import re
import logging
import json
import requests
from urllib.parse import urlparse, parse_qs
from transcripto.utils.http import verify_response
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

            html = html_response.text

            patterns = [
                {"key": "ytInitialPlayerResponse", "pattern": r'<script nonce="[^"]+">var ytInitialPlayerResponse = ({.*?});<\/script>'},
            ]

            extracted_data = {}
            for item in patterns:
                match = re.search(item["pattern"], html, re.DOTALL)
                if match:
                    json_str = match.group(1).strip()
                    try:
                        extracted_data[item["key"]] = json.loads(json_str)
                    except json.JSONDecodeError as e:
                        logging.error(f"Error decoding JSON for {item['key']}: {e}")
                        raise

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
