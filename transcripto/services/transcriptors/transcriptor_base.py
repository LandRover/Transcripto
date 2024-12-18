from abc import ABC, abstractmethod

class TranscriptorBase(ABC):
    @abstractmethod
    def transcribe(self, mp3_path, temp_dir, title, language, force):
        pass