import re
import logging
import json
import requests
from urllib.parse import urlparse, parse_qs
from transcripto.utils.http import verify_response
from .models import ApplePodcastsURL, ApplePodcastsDownloadItem

class ApplePodcastsAPI:
    APPLE_PODCASTS_HOME_PAGE_URL = "https://podcasts.apple.com/"


    def __init__(self):
        self.__apply_requests_session()


    def __apply_requests_session(self):
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "text/html",
            "accept-language": "en-US",
            "content-type": "text/html",
            "origin": self.APPLE_PODCASTS_HOME_PAGE_URL,
            "referer": self.APPLE_PODCASTS_HOME_PAGE_URL,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/131.0.0.0 Safari/537.36",
        })


    def get_episode_metadata(self, url: str) -> list[ApplePodcastsDownloadItem]:
        try:
            html_response = requests.get(url, stream=True)
            verify_response(html_response)

            html = html_response.text

            patterns = [
                {"key": "schema_episode", "pattern": r'<script id=schema:episode type="application/ld\+json">(.*?)</script>'},
                {"key": "serialized_server_data", "pattern": r'<script type="application/json" id="serialized-server-data">(.*?)</script>'}
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
        
        return ApplePodcastsDownloadItem(
            episode_info = extracted_data["schema_episode"],
            episode_audio_url = extracted_data["serialized_server_data"][0]["data"]["shelves"][0]["items"][0]["contextAction"]["episodeOffer"]["streamUrl"],
        )


    def extract_media_from_url(self, url) -> list[ApplePodcastsURL]:
        parsed_url = urlparse(url)

        # Extract the episode name and show ID from the path
        path = parsed_url.path
        path_parts = path.strip('/').split('/')
        
        if len(path_parts) >= 3:
            episode_name = path_parts[2]
            episode_show_id = path_parts[3]
        else:
            episode_name = None
            episode_show_id = None

        # Extract the 'i' parameter (episode ID) from the query string
        query_params = parse_qs(parsed_url.query)
        episode_id = query_params.get('i', [None])[0]

        return ApplePodcastsURL(
            episode_id = episode_id,
            episode_name = episode_name,
            episode_show_id = episode_show_id
        )