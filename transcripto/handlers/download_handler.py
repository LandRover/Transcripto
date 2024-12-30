import os
import time
import logging
from pathlib import Path
from config import TEMP_DIR, OUTPUT_DIR
from transcripto.services.download.download_factory import DownloadFactory
from transcripto.utils.file_utils import save_to_file, get_output_file
from transcripto.handlers.metadata_handler import fetch_audio_metadata


def process_download(url, force=False):
    start_time = time.time()

    logging.info(f"Starting download {url}...")

    downloader = DownloadFactory.get_download_engine(url)
    target_filename = downloader.get_episode_id(url)

    base_filename = f"{target_filename}_raw"
    output_file = get_output_file(base_filename, "mp3")

    # cached file already exists, use it.
    if not force and os.path.exists(output_file):
        logging.info(f"Using existing cached file: {output_file}")
        audio_metadata = fetch_audio_metadata(output_file)
        return target_filename, output_file, audio_metadata

    # Select the download strategy
    download_output = downloader.download(
        url,
        Path(TEMP_DIR)
    )
    
    logging.info(f"Download completed in {time.time() - start_time:.2f} seconds.")
    save_to_file(output_file, download_output)
    audio_metadata = fetch_audio_metadata(output_file)
    logging.info(f"Download saved to {output_file}")

    return target_filename, output_file, audio_metadata
