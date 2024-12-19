import os
import time
import logging
from transcripto.services.download.download_factory import DownloadFactory
from transcripto.utils.file_utils import save_to_file, get_output_file


def process_download(url, title, force=False):
    logging.info(f"Starting download {title}...")
    start_time = time.time()

    base_filename = f"{title}_raw"
    output_file = get_output_file(base_filename, "mp3")

    if not force and os.path.exists(output_file):
        logging.info(f"Using existing summary: {output_file}")
        return output_file

    # Select the transcriptor strategy
    downloader = DownloadFactory.get_download_engine(url)
    download_output = downloader.download(
        url,
        title,
    )
    
    logging.info(f"Download completed in {time.time() - start_time:.2f} seconds.")
    save_to_file(output_file, download_output)
    logging.info(f"Download saved to {output_file}")

    return output_file
