import os
import io
import logging
from openai import OpenAI
from .text_to_speech_base import TextToSpeechBase

class OpenAITTS1(TextToSpeechBase):
    def generate_text_to_speech(self, text, tts_model="tts-1", voice="alloy", format="mp3", force=False):
        try:
            client = OpenAI(
                api_key = os.environ.get("OPENAI_API_KEY"),
            )

            response = client.audio.speech.create(
                model = tts_model,
                voice = voice,
                input = text
            )

            # Stream the response content into a buffer
            buffer = io.BytesIO()
            for chunk in response.iter_bytes():  # Stream MP3 data chunks
                buffer.write(chunk)
            
            buffer.seek(0)  # Reset buffer pointer
            mp3_bytes = buffer.read()  # Return the binary MP3 content
            
            return mp3_bytes
        except Exception as e:
            logging.error(f"text-to-speech failed attempts: {e}")
            raise RuntimeError(f"Error generating speech: {e}")
