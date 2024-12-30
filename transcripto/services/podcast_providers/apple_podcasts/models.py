from dataclasses import dataclass


@dataclass
class ApplePodcastsURL:
    episode_id: str = None
    episode_name: str = None
    episode_show_id: str = None


@dataclass
class ApplePodcastsDownloadItem:
    episode_info: dict = None
    episode_audio_url: str = None

