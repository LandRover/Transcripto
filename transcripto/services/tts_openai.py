import os
import logging
import base64
from openai import OpenAI

def tts_openai(text, tts_model="gpt-4o-audio-preview", voice="alloy", format="mp3", force=False):
    try:
        client = OpenAI(
            api_key = os.environ.get("OPENAI_API_KEY"),
        )

        prompt = (f"You are a helpful hebrew speaking assistant that can generate audio from text."
                    "\nSpeak in a Hebrew without accent."
                 )

        completion = client.chat.completions.create(
            model = tts_model,
            modalities = ["text", "audio"],
            audio = {
                "voice": voice,
                "format": format
            },
            messages = [
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": text,
                }
            ],
        )

        mp3_bytes = base64.b64decode(completion.choices[0].message.audio.data)
        return mp3_bytes
    except Exception as e:
        logging.error(f"text-to-speech failed attempts: {e}")
        raise RuntimeError(f"Error generating speech: {e}")
