import os
import logging
import time
from transcripto.services.tts_openai import tts_gpt_openai, tts_tts1_openai
from transcripto.services.tts_gtts import tts_gtts
from transcripto.utils.file_utils import save_to_file, get_output_file

def process_tts(
        title, text, tts_model="gpt-4o-audio-preview", force=False, voice="alloy", format="mp3"
):
    start_time = time.time()
    logging.info(f"Starting TTS using {tts_model} model...")

    base_filename = f"{title}_{tts_model}_tts"
    output_file = get_output_file(base_filename, "mp3")

    if not force and os.path.exists(output_file):
        logging.info(f"Raw text-to-speech file already exists: {output_file}, using it.")
        with open(output_file, "r", encoding="utf-8") as f:
            return f.read()

    tts_output_mp3_bytes = tts_gpt_openai(
        text,
        tts_model,
        voice,
        format,
        force
    )

    logging.info(f"text-to-speech completed in {time.time() - start_time:.2f} seconds.")
    save_to_file(output_file, tts_output_mp3_bytes)
    logging.info(f"Raw text-to-speech saved to {output_file}")

    return tts_output_mp3_bytes
