import re
import json
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
    EPISODE_EMBED_URL = "https://open.spotify.com/embed/episode/{item_id}"
    EPISODE_AUDIO_API_URL = "https://spclient.wg.spotify.com/soundfinder/v1/unauth/episode/{item_id}/com.widevine.alpha?market=from_token"

    HEADERS = {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": SPOTIFY_HOME_PAGE_URL,
            "referer": SPOTIFY_HOME_PAGE_URL + "/",
            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
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
            server_time = int(1000 * server_time_response.json().get("serverTime"))
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


    def get_episode_metadata(self, media_id: str) -> SpotifyDownloadItem:
        self.__refresh_access_token()
        
        # Get metadata from embed page (no rate limits, no auth needed)
        embed_response = self.session.get(
            self.EPISODE_EMBED_URL.format(item_id=media_id),
            headers={"accept": "text/html"}
        )
        embed_response.encoding = 'utf-8'
        verify_response(embed_response)
        
        # Extract __NEXT_DATA__ JSON from embed page
        next_data_match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            embed_response.text,
            re.DOTALL
        )
        if not next_data_match:
            raise Exception("Could not parse episode metadata from embed page")
        
        next_data = json.loads(next_data_match.group(1))
        entity = next_data.get('props', {}).get('pageProps', {}).get('state', {}).get('data', {}).get('entity', {})
        
        if not entity:
            raise Exception("Episode entity not found in embed data")

        # Get audio URL from audio API
        episode_audio = self.session.get(self.EPISODE_AUDIO_API_URL.format(item_id=media_id))
        episode_audio.encoding = 'utf-8'
        verify_response(episode_audio)

        audio_data = episode_audio.json()
        episode_audio_url = audio_data["url"][0] if audio_data.get("url") else None
        
        # Extract show ID from relatedEntityUri (format: spotify:show:ID)
        show_uri = entity.get("relatedEntityUri", "")
        show_id = show_uri.split(":")[-1] if show_uri else None
        
        # Get cover image (prefer larger size)
        cover_images = entity.get("relatedEntityCoverArt", []) or entity.get("visualIdentity", {}).get("image", [])
        cover_url = cover_images[1]["url"] if len(cover_images) > 1 else (cover_images[0]["url"] if cover_images else None)
        
        # Parse release date
        release_date = entity.get("releaseDate", {}).get("isoString", "")[:10] if entity.get("releaseDate") else None

        episode_info = {
            "episode": {
                "id": entity.get("id"),
                "title": entity.get("name") or entity.get("title"),
                "description": entity.get("description", ""),
                "duration": entity.get("duration"),
                "date": release_date,
                "url": f"https://open.spotify.com/episode/{entity.get('id')}",
            },
            "show": {
                "id": show_id,
                "author": entity.get("subtitle", ""),  # subtitle contains show name/author
                "title": entity.get("subtitle", ""),
                "description": "",
                "cover": cover_url,
                "url": f"https://open.spotify.com/show/{show_id}" if show_id else None,
                "total_episodes": None,
            },
        }

        return SpotifyDownloadItem(
            episode_info=episode_info,
            episode_audio_url=episode_audio_url,
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
