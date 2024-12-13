import os
import logging
import time
from services.audio_processing import transcribe_audio
from utils.file_utils import save_to_file, get_output_file

def process_transcription(
        audio_url, temp_dir, title, ext="mp3", transcript_engine="speech_recognition", language="en-US", min_silence_len=1000, silence_thresh=-14, force=False
):
    start_time = time.time()
    logging.info(f"Starting transcription using {transcript_engine} engine...")

    base_filename = f"{title}_{transcript_engine}_transcript"
    output_file = get_output_file(base_filename, "txt")

    if not force and os.path.exists(output_file):
        logging.info(f"Raw transcription file already exists: {output_file}, using it.")
        with open(output_file, "r", encoding="utf-8") as f:
            return f.read()

    transcription_output_text = transcribe_audio(
        audio_url,
        temp_dir,
        title,
        language,
        min_silence_len,
        silence_thresh,
        force
    )

    logging.info(f"Transcription completed in {time.time() - start_time:.2f} seconds.")
    save_to_file(output_file, transcription_output_text)
    logging.info(f"Raw transcription saved to {output_file}")

    return transcription_output_text
