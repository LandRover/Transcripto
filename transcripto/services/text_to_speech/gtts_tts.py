import io
import logging
from gtts import gTTS

from .text_to_speech_base import TextToSpeechBase

class gTTS(TextToSpeechBase):
    def generate_text_to_speech(self, text, tts_model="", voice="alloy", format="mp3", force=False):
        try:
            tts = gTTS(text, lang = 'iw')

            # Save MP3 to in-memory buffer
            buffer = io.BytesIO()
            tts.write_to_fp(buffer)  # Use write_to_fp to save MP3 data into the buffer
            buffer.seek(0)  # Move to the start of the buffer
            mp3_bytes = buffer.read()
            return mp3_bytes
        except Exception as e:
            logging.error(f"text-to-speech failed attempts: {e}")
            raise RuntimeError(f"Error generating speech: {e}")
