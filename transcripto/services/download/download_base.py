from abc import ABC, abstractmethod
from pathlib import Path

class DownloadBase(ABC):
    @abstractmethod
    def get_episode_id(self, url):
        pass


    @abstractmethod
    def download(self, url: str, temp_path: Path):
        pass
