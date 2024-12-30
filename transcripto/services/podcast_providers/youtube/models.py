from dataclasses import dataclass


@dataclass
class YoutubeURL:
    id: str = None
    type: str = None


@dataclass
class YoutubeDownloadItem:
    episode_info: dict = None
    episode_audio_url: str = None

