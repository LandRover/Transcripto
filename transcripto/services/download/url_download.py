import logging
import requests
from pathlib import Path
from .download_base import DownloadBase
from transcripto.utils.file import extract_filename_from_url

class URLDownload(DownloadBase):

    def __init__(self):
        self.__apply_requests_session()


    def __apply_requests_session(self):
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "*/*",
            "accept-language": "en-US",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        })
    
    def get_episode_id(self, url):
        filename = extract_filename_from_url(url)

        return filename


    def download(self, url: str, temp_path: Path, headers: dict = None):
        logging.info(f"URLDownload Starting download {url}...")

        # local path handler, move elsewhere?
        # if os.path.isfile(url):
        #    logging.info(f"Using local file: {url}")
        #    with open(url, "rb") as f:
        #        return f.read()

        logging.info(f"Downloading file from URL: {url}")

        try:
            response = self.session.get(url, stream=True, headers=headers)
            response.raise_for_status()
            logging.info(f"Download completed: {url}")

            return response.content
        
        except requests.RequestException as e:
            logging.error(f"Failed to download file: {e}")
            raise
