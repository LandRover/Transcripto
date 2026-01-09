import re
import json
import logging
import requests
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
            "origin": self.YOUTUBE_HOME_PAGE_URL,
            "referer": self.YOUTUBE_HOME_PAGE_URL,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/131.0.0.0 Safari/537.36",
        })


    def _extract_json_object(self, text: str, start_marker: str) -> dict:
        """Extract a JSON object from text by finding balanced braces."""
        start_idx = text.find(start_marker)
        if start_idx == -1:
            raise ValueError(f"Marker '{start_marker}' not found in text")
        
        # Find the opening brace after the marker
        json_start = text.find('{', start_idx)
        if json_start == -1:
            raise ValueError("No JSON object found after marker")
        
        # Count braces to find the complete JSON object
        brace_count = 0
        in_string = False
        escape_next = False
        
        for i, char in enumerate(text[json_start:], start=json_start):
            if escape_next:
                escape_next = False
                continue
            if char == '\\' and in_string:
                escape_next = True
                continue
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            if in_string:
                continue
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_str = text[json_start:i + 1]
                    return json.loads(json_str)
        
        raise ValueError("Unbalanced braces in JSON object")


    def get_episode_metadata(self, url: str) -> list[YoutubeDownloadItem]:
        try:
            html_response = self.session.get(url, stream=True)
            verify_response(html_response)

            # Extract ytInitialPlayerResponse using balanced brace matching
            player_response = self._extract_json_object(
                html_response.text, 
                'var ytInitialPlayerResponse'
            )
            
            extracted_data = {"ytInitialPlayerResponse": player_response}

            episode_info = {
                "episode": {
                    "id": extracted_data["ytInitialPlayerResponse"].get("videoDetails", {}).get("videoId"),
                    "title": extracted_data["ytInitialPlayerResponse"].get("microformat", {}).get("playerMicroformatRenderer", {}).get("title").get("simpleText"),
                    "description": extracted_data["ytInitialPlayerResponse"].get("microformat", {}).get("playerMicroformatRenderer", {}).get("description").get("simpleText"),
                    "duration": extracted_data["ytInitialPlayerResponse"].get("microformat", {}).get("playerMicroformatRenderer", {}).get("lengthSeconds"),
                    "genre": extracted_data["ytInitialPlayerResponse"].get("microformat", {}).get("playerMicroformatRenderer", {}).get("category"),
                    "date": extracted_data["ytInitialPlayerResponse"].get("microformat", {}).get("playerMicroformatRenderer", {}).get("uploadDate"),
                    "views": extracted_data["ytInitialPlayerResponse"].get("microformat", {}).get("playerMicroformatRenderer", {}).get("viewCount"),
                },
                "show": {
                    "id": extracted_data["ytInitialPlayerResponse"].get("microformat", {}).get("playerMicroformatRenderer").get("externalChannelId"),
                    "author": extracted_data["ytInitialPlayerResponse"].get("microformat", {}).get("playerMicroformatRenderer").get("ownerChannelName"),
                    "cover": extracted_data["ytInitialPlayerResponse"].get("microformat", {}).get("playerMicroformatRenderer").get("thumbnail").get("thumbnails").pop().get("url"),
                    "url": extracted_data["ytInitialPlayerResponse"].get("microformat", {}).get("playerMicroformatRenderer").get("ownerProfileUrl"),
                },
            }

        except requests.RequestException as e:
            logging.error(f"Failed to fetch episode data: {e}")
            raise
        
        return YoutubeDownloadItem(
            episode_info = episode_info,
            episode_audio_url = url,
        )


    def extract_media_from_url(self, url) -> list[YoutubeURL]:
        youtube_regex = r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:[&?\/]|$)'
        match = re.search(youtube_regex, url)

        return YoutubeURL(
            id = match.group(1) if match else None,
        )
