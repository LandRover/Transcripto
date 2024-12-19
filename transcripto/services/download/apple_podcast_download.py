import os
import logging
import requests
from .download_base import DownloadBase

class ApplePodcastDownload(DownloadBase):

    def download(self, url):
        return True