import os
import logging
import requests

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
