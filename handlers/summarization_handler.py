import os
import time
import logging
from services.openai_service import summarize_text_with_retry
from utils.file_utils import save_to_file, get_output_file


def process_summarization(transcription, force=False):
    logging.info("Starting summarization...")
    start_time = time.time()

    base_filename = "summary"
    output_file = get_output_file(base_filename, "txt")

    if not force and os.path.exists(output_file):
        logging.info(f"Using existing summary: {output_file}")
        with open(output_file, "r", encoding="utf-8") as f:
            return f.read()

    summary = summarize_text_with_retry(transcription)
    logging.info(f"Summarization completed in {time.time() - start_time:.2f} seconds.")
    save_to_file(output_file, summary)
    logging.info(f"Summary saved to {output_file}")
    return summary
