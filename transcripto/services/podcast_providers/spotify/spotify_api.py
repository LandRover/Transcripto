import re
import time
import requests
from transcripto.utils.http import verify_response
from .models import SpotifyURL, SpotifyDownloadItem

class SpotifyAPI:
    SPOTIFY_TOKEN_URL = 'https://open.spotify.com/get_access_token?reason=transport&productType=web-player'
    SPOTIFY_APP_VERSION = "1.2.54.219.g19a93a5d" # 24/12/2024
    SPOTIFY_HOME_PAGE_URL = "https://open.spotify.com"
    EPISODE_INFO_API_URL = "https://api.spotify.com/v1/{type}/{item_id}"
    EPISODE_AUDIO_API_URL = "https://spclient.wg.spotify.com/soundfinder/v1/unauth/episode/{item_id}/com.widevine.alpha?market=from_token"


    def __init__(self):
        self.__apply_requests_session()


    def __apply_requests_session(self):
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "application/json",
            "accept-language": "en-US",
            "app-platform": "WebPlayer",
            "content-type": "application/json",
            "origin": self.SPOTIFY_HOME_PAGE_URL,
            "referer": self.SPOTIFY_HOME_PAGE_URL,
            "spotify-app-version": self.SPOTIFY_APP_VERSION,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/131.0.0.0 Safari/537.36",
        })
        self.__get_access_token()


    def __get_access_token(self):
        token_request = self.session.get(url = self.SPOTIFY_TOKEN_URL)

        if token_request.status_code != 200:
            return None
        
        token_json = token_request.json()
        self.session_info = token_json
        access_token = token_json.get('accessToken')

        self.session.headers.update({
            "Authorization": f"Bearer {access_token}",
        })

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
        verify_response(episode_info)

        episode_audio = self.session.get(self.EPISODE_AUDIO_API_URL.format(item_id = media_id))
        verify_response(episode_audio)

        episode_audio_url = episode_audio.json()["url"].pop(0)

        return SpotifyDownloadItem(
            episode_info = episode_info.json(),
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
