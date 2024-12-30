from dataclasses import dataclass


@dataclass
class SpotifyURL:
    id: str = None
    type: str = None


@dataclass
class SpotifyDownloadItem:
    episode_info: dict = None
    episode_audio: dict = None

