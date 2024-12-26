import re
import logging
from .url_download import URLDownload
from .spotify_download import SpotifyDownload
from .youtube_download import YoutubeDownload
from .apple_podcast_download import ApplePodcastDownload
from .pocketcasts_download import PocketCastsDownload

class DownloadFactory:
    # Mapping of patterns to download engine classes
    download_engines_mapping = [
        (re.compile(r'^https?://(open\.)?spotify\.com/.*'), SpotifyDownload),
        (re.compile(r'^https?://(www\.)?youtube\.com/.*'), YoutubeDownload),
        (re.compile(r'^https?://(podcasts\.)?apple\.com/.*'), ApplePodcastDownload),
        (re.compile(r'^https://pca\.st/episode/[a-f0-9\-]+$'), PocketCastsDownload),
        (re.compile(r'^https://.*\.mp3$'), URLDownload),
    ]


    @staticmethod
    def get_download_engine(url):
        for pattern, download_cls in DownloadFactory.download_engines_mapping:
            if pattern.match(url):
                logging.info(f"Detected pattern: {pattern}")
                return download_cls()

        raise ValueError(f"Unsupported download URL: {url}")

