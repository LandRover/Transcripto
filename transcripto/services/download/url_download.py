import os
import logging
import requests
from .download_base import DownloadBase

class URLDownload(DownloadBase):

    def download(self, path, title):
        logging.info(f"Starting dowload of {title} in path: {path}...")

        if os.path.isfile(path):
            logging.info(f"Using local file: {path}")
            with open(path, "rb") as f:
                return f.read()  # Read and return the file content

        logging.info(f"Downloading file from URL: {path}")

        try:
            response = requests.get(path, stream = True)
            response.raise_for_status()
            logging.info(f"Download completed: {path}")
            return response.content
        except requests.RequestException as e:
            logging.error(f"Failed to download file: {e}")
            raise
