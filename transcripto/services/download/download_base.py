from abc import ABC, abstractmethod

class DownloadBase(ABC):
    @abstractmethod
    def get_filename(self, url):
        pass

    @abstractmethod
    def download(self, url):
        pass