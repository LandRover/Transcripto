from dataclasses import dataclass


@dataclass
class PocketCastsURL:
    id: str = None
    type: str = None


@dataclass
class PocketCastsDownloadItem:
    episode_info: dict = None
    episode_audio_url: str = None

