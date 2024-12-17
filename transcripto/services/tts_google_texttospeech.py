import os
import logging
from google.cloud import texttospeech

def tts_google_texttospeech(text, tts_model="", voice="alloy", format="mp3", force=False):
    try:
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code="he-IL", 
            ssml_gender = texttospeech.SsmlVoiceGender.FEMALE
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding = texttospeech.AudioEncoding.MP3
        )
        
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        mp3_bytes = response.audio_content
        return mp3_bytes
    except Exception as e:
        logging.error(f"text-to-speech failed attempts: {e}")
        raise RuntimeError(f"Error generating speech: {e}")
