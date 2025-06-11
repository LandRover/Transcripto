import re
import time
import requests
from syrics.totp import TOTP
from transcripto.utils.http import verify_response
from .models import SpotifyURL, SpotifyDownloadItem
from transcripto.exceptions import TOTPGenerationException

class SpotifyAPI:
    SPOTIFY_HOME_PAGE_URL = "https://open.spotify.com"
    SPOTIFY_TOKEN_URL = "https://open.spotify.com/api/token"
    SPOTIFY_SERVER_TIME_URL = "https://open.spotify.com/api/server-time"
    SPOTIFY_APP_VERSION = "1.2.66.328.g8b32269e" # 11/06/2025
    EPISODE_INFO_API_URL = "https://api.spotify.com/v1/{type}/{item_id}"
    EPISODE_AUDIO_API_URL = "https://spclient.wg.spotify.com/soundfinder/v1/unauth/episode/{item_id}/com.widevine.alpha?market=from_token"

    HEADERS = {
            "accept": "application/json",
            "accept-language": "en-US",
            "content-type": "application/json",
            "origin": SPOTIFY_HOME_PAGE_URL,
            "referer": SPOTIFY_HOME_PAGE_URL,
            "priority": "u=1, i",
            "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "spotify-app-version": SPOTIFY_APP_VERSION,
            "app-platform": "WebPlayer",
        }


    def __init__(self):
        self.totp = TOTP()
        self.__apply_requests_session()


    def __apply_requests_session(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.__get_access_token()


    def __get_access_token(self):
        try:
            server_time_response = self.session.get(self.SPOTIFY_SERVER_TIME_URL)
            server_time = 1e3 * server_time_response.json().get("serverTime")
            totp = self.totp.generate(timestamp=server_time)

            params = {
                "reason": "init",
                "productType": "web-player",
                "totp": totp,
                "totpVer": str(self.totp.version),
                "ts": str(server_time),
            }

        except Exception as e:
            raise TOTPGenerationException("Error generating TOTP, retry!") from e

        token_request = self.session.get(self.SPOTIFY_TOKEN_URL, params=params)
        token = token_request.json()
        self.session_info = token
        access_token = token.get('accessToken')

        self.session.headers['authorization'] = f"Bearer {access_token}"

        return access_token

        
    def __refresh_access_token(self):
        timestamp_session_expire = int(self.session_info["accessTokenExpirationTimestampMs"])

        timestamp_now = time.time() * 1000
        if timestamp_now < timestamp_session_expire:
            return
        
        return self.get_access_token()


    def get_episode_metadata(self, media_id: str) -> list[SpotifyDownloadItem]:
        self.__refresh_access_token()
        
        episode_info = self.session.get(self.EPISODE_INFO_API_URL.format(type = "episodes", item_id = media_id))
        episode_info.encoding = 'utf-8'
        verify_response(episode_info)

        episode_audio = self.session.get(self.EPISODE_AUDIO_API_URL.format(item_id = media_id))
        episode_audio.encoding = 'utf-8'
        verify_response(episode_audio)

        episode_audio_url = episode_audio.json()["url"].pop(0)
        extracted_data = episode_info.json()

        episode_info = {
            "episode": {
                "id": extracted_data.get("id"),
                "title": extracted_data.get("name"),
                "description": extracted_data.get("description"),
                "duration": extracted_data.get("duration_ms"),
                "date": extracted_data.get("release_date"),
                "url": extracted_data.get("external_urls").get("spotify"),
            },
            "show": {
                "id": extracted_data.get("show", {}).get("id"),
                "author": extracted_data.get("show", {}).get("publisher"),
                "title": extracted_data.get("show", {}).get("name"),
                "description": extracted_data.get("show", {}).get("description"),
                "cover": extracted_data.get("show", {}).get("images").pop(0).get("url"),
                "url": extracted_data.get("show", {}).get("external_urls").get("spotify"),
                "total_episodes": extracted_data.get("show", {}).get("total_episodes"),
            },
        }

        return SpotifyDownloadItem(
            episode_info = episode_info,
            episode_audio_url = episode_audio_url,
        )


    def extract_media_from_url(self, url) -> list[SpotifyURL]:
        URL_RE = r"(episode)/(\w{22})"
        url_regex_result = re.search(URL_RE, url)

        if url_regex_result is None:
            raise Exception("Invalid URL")
        
        return SpotifyURL(
            id = url_regex_result.group(2),
            type = url_regex_result.group(1),
        )
