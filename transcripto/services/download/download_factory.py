import re
import logging
from .url_download import URLDownload
from .spotify_download import SpotifyDownload
from .youtube_download import YoutubeDownload
from .apple_podcast_download import ApplePodcastDownload

class DownloadFactory:
    # Mapping of patterns to download engine classes
    download_engines_mapping = [
        (re.compile(r'^https?://(www\.)?spotify\.com/.*'), SpotifyDownload),
        (re.compile(r'^https?://(www\.)?youtube\.com/.*'), YoutubeDownload),
        (re.compile(r'^https?://(www\.)?apple\.com/podcast/.*'), ApplePodcastDownload),
        (re.compile(r'^https?://.*'), URLDownload),  # Fallback for generic URLs
    ]

    @staticmethod
    def get_download_engine(url):
        for pattern, download_cls in DownloadFactory.download_engines_mapping:
            if pattern.match(url):
                logging.info(f"Detected pattern: {pattern}")
                return download_cls()
        raise ValueError(f"Unsupported download URL: {url}")
