import os
import logging
import requests
from .download_base import DownloadBase

class YoutubeDownload(DownloadBase):

    def download(self, url):
        return True