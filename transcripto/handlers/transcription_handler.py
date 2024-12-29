import os
import logging
import time
from transcripto.services.transcriptors.transcriptor_factory import TranscriptorFactory
from transcripto.utils.file_utils import save_to_file, get_output_file
from transcripto.utils.text import split_text_into_paragraphs

def process_transcription(
        audio_url, temp_dir, title, ext="mp3", transcript_engine="speech_recognition", language="en-US", min_silence_len=1000, silence_thresh=-14, force=False
):
    start_time = time.time()
    logging.info(f"Starting transcription using {transcript_engine} model...")

    base_filename = f"{title}_{transcript_engine}_transcript"
    output_file = get_output_file(base_filename, "txt")

    if not force and os.path.exists(output_file):
        logging.info(f"Raw transcription file already exists: {output_file}, using it.")
        with open(output_file, "r", encoding="utf-8") as f:
            return f.read()

    # Select the transcriptor strategy
    transcriptor = TranscriptorFactory.get_transcriptor(transcript_engine)
    transcription_output = transcriptor.transcribe(audio_url)
    transcription_output_text = transcription_output["text"]

    logging.info(f"Transcription completed in {time.time() - start_time:.2f} seconds.")

    formatted_text = split_text_into_paragraphs(transcription_output_text)
    
    save_to_file(output_file, formatted_text)

    logging.info(f"Raw transcription saved to {output_file}")

    return formatted_text
