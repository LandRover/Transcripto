import logging
import whisper
import ssl
from .transcriptor_base import TranscriptorBase

ssl._create_default_https_context = ssl._create_unverified_context

class WhisperTranscriptor(TranscriptorBase):
    def transcribe(
        self, mp3_path, temp_dir, title, language="en-US", force=False
    ):
        """
        Transcribes an MP3 file into text with wisper processing, logging, and error handling.

        Args:
            mp3_path (str): Path to the MP3 file.
            temp_dir (str): Directory for temporary chunk files.
            force (bool): Force reprocessing of existing chunks.

        Returns:
            str: Final transcription text.
        """

        # Load audio
        try:
            model = whisper.load_model("turbo")
            result = model.transcribe(mp3_path, language="he", fp16=False, verbose=False)
            transcription = result["text"]

        except Exception as e:
            logging.error(f"Failed to transcribe audio file: {e}")
            return ""


        return transcription
