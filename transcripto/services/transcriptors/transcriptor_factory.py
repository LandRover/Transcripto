from .speech_recognition_transcriptor import SpeechRecognitionTranscriptor
from .wisper_transcriptor import WhisperTranscriptor


class TranscriptorFactory:
    transcriptor_engines_mapping = {
        "speech_recognition": SpeechRecognitionTranscriptor,
        "wisper": WhisperTranscriptor,
    }

    @staticmethod
    def get_transcriptor(transcriptor_engine):
        transcriptor_cls = TranscriptorFactory.transcriptor_engines_mapping.get(transcriptor_engine)
        if not transcriptor_cls:
            raise ValueError(f"Unsupported transcription engine: {transcriptor_engine}")
        return transcriptor_cls()

