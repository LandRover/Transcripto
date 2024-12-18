import os
import logging
import time
from transcripto.services.text_to_speech.text_to_speech_factory import TextToSpeechFactory
from transcripto.utils.file_utils import save_to_file, get_output_file

def process_tts(
        title, text, tts_engine="openai_gpt", tts_model="gpt-4o-audio-preview", force=False, voice="alloy", format="mp3"
):
    start_time = time.time()
    logging.info(f"Starting TTS using {tts_engine} {tts_model} model...")

    base_filename = f"{title}_{tts_engine}_{tts_model}_tts"
    output_file = get_output_file(base_filename, "mp3")

    if not force and os.path.exists(output_file):
        logging.info(f"Raw text-to-speech file already exists: {output_file}, using it.")
        with open(output_file, "rb") as f:
            return f.read()

    # Select the tts strategy
    tts = TextToSpeechFactory.get_tts(tts_engine)
    tts_output_mp3_bytes = tts.generate_text_to_speech(
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
