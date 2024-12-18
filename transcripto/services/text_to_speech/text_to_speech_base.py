from abc import ABC, abstractmethod

class TextToSpeechBase(ABC):
    @abstractmethod
    def generate_text_to_speech(self, title, text, tts_engine, tts_model, force, voice, format):
        pass
