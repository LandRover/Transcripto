from abc import ABC, abstractmethod

class TranscriptorBase(ABC):
    @abstractmethod
    def transcribe(self, audio_path):
        pass