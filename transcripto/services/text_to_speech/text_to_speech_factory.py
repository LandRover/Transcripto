from .gtts_tts import gTTS
from .google_texttospeech_tts import Google_TextToSpeech
from .openai_gpt_tts import OpenAIGPT
from .openai_tts1_tts import OpenAITTS1

class TextToSpeechFactory:
    tts_engines_mapping = {
        "gtts": gTTS,
        "google_texttospeech": Google_TextToSpeech,
        "openai_gpt": OpenAIGPT,
        "openai_tts1": OpenAITTS1,
    }

    @staticmethod
    def get_tts(tts_engine):
        tts_cls = TextToSpeechFactory.tts_engines_mapping.get(tts_engine)
        if not tts_cls:
            raise ValueError(f"Unsupported text-to-speech engine: {tts_engine}")
        return tts_cls()

