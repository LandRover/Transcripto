from dataclasses import dataclass


@dataclass
class SpotifyURL:
    id: str = None
    type: str = None


@dataclass
class SpotifyDownloadItem:
    episode_metadata: dict = None

