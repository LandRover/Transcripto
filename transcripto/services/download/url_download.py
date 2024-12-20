import os
import logging
import requests
from .download_base import DownloadBase
from transcripto.utils.file_utils import extract_filename_from_url

class URLDownload(DownloadBase):
    def get_filename(self, url):
        filename = extract_filename_from_url(url)
        
        return filename


    def download(self, url):
        logging.info(f"Starting dowload of {url} in path: {url}...")

        # local path handler, move elsewhere?
        if os.path.isfile(url):
            logging.info(f"Using local file: {url}")
            with open(url, "rb") as f:
                return f.read()

        logging.info(f"Downloading file from URL: {url}")

        try:
            response = requests.get(url, stream = True)
            response.raise_for_status()
            logging.info(f"Download completed: {url}")

            return response.content
        
        except requests.RequestException as e:
            logging.error(f"Failed to download file: {e}")
            raise
