import os
import logging
import requests
from utils.file_utils import download_file
from urllib.parse import urlparse

def validate_and_download(input_path, temp_dir):
    try:
        if os.path.exists(input_path):
            logging.info(f"Using local file: {input_path}")
            return input_path

        validate_audio_file(input_path)
        logging.info("Starting MP3 file download/check...")
        return download_mp3(input_path, temp_dir)
    except Exception as e:
        logging.error(f"Audio validation or download failed: {e}")
        raise


def validate_audio_file(filepath):
    parsed = urlparse(filepath)
    if parsed.scheme in ["http", "https"]:
        # URL detected, skip local file checks
        return
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    if not filepath.lower().endswith(".mp3"):
        raise ValueError(f"Invalid file format. Expected .mp3, got: {filepath}")


def download_mp3(url_or_path, temp_dir):
    if os.path.isfile(url_or_path):
        logging.info(f"Using local file: {url_or_path}")
        return url_or_path

    filename = os.path.join(temp_dir, os.path.basename(url_or_path))
    if os.path.exists(filename):
        logging.info(f"File already exists: {filename}")
        return filename

    logging.info(f"Downloading file from URL: {url_or_path}")
    try:
        response = requests.get(url_or_path, stream=True)
        response.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        logging.info(f"Download completed: {filename}")
    except requests.RequestException as e:
        logging.error(f"Failed to download file: {e}")
        raise
    return filename