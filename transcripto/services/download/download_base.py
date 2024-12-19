from abc import ABC, abstractmethod

class DownloadBase(ABC):
    @abstractmethod
    def download(self, url):
        pass
