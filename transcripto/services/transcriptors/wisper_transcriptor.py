import time
import logging
import whisper
import torch
from tqdm import tqdm
import ssl
from .transcriptor_base import TranscriptorBase

ssl._create_default_https_context = ssl._create_unverified_context

class WhisperTranscriptor(TranscriptorBase):
    def transcribe(self, audio_path):
        """
        Transcribes an audio file using the Whisper model with a progress bar.

        Args:
            audio_path: Path to the audio file to transcribe.

        Returns:
            dict: The full transcription result containing text, language, and other metadata.
        """
        start_time = time.time()

        logging.info("Loading Whisper model")
        model = whisper.load_model("turbo")

        if torch.cuda.is_available():
            logging.info("Using GPU")
        else:
            logging.info("Using CPU")

        logging.info(f"Loading audio {audio_path}...")
        audio = whisper.load_audio(audio_path)

        logging.info("Creating mel spectrogram...")
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        total_frames = mel.shape[-1]  # Total number of time frames in the Mel spectrogram
        logging.info(f"Mel spectrogram shape: {mel.shape}, Total number of time frames: {total_frames}")  # Debugging: Check shape

        # Verify the mel spectrogram shape
        if mel.shape[0] != 80:
            raise ValueError(f"Expected mel spectrogram to have 80 channels, but got {mel.shape[0]}.")

        # Set decoding options
        options = whisper.DecodingOptions(fp16=False)

        logging.info("Starting transcription...")
        result = model.transcribe(audio, verbose=False)
        full_text = result["text"]
        detected_language = result["language"]

        logging.info(f"Transcription complete for {audio_path}!")

        output = {
            "text": full_text,
            "detected_language": detected_language,
            "duration_seconds": f"{time.time() - start_time:.2f}",
        }

        return output
