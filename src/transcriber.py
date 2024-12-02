import os
import logging
from pydub import AudioSegment
from pydub.silence import split_on_silence
import speech_recognition as sr

def transcribe_audio(mp3_path, temp_dir, chunk_size=1024):
    """Transcribes an MP3 file into text."""
    audio = AudioSegment.from_mp3(mp3_path)

    # Split the audio into chunks based on silence
    logging.info("Splitting audio into chunks...")
    chunks = split_on_silence(
        audio,
        min_silence_len=1000,  # Minimum silence length in ms
        silence_thresh=audio.dBFS - 14,  # Silence threshold
        keep_silence=500  # Keep some silence
    )

    recognizer = sr.Recognizer()
    transcription = ""

    for i, chunk in enumerate(chunks):
        chunk_path = os.path.join(temp_dir, f"chunk_{i}.wav")
        chunk.export(chunk_path, format="wav")
        logging.info(f"Processing chunk {i}: {chunk_path}")

        with sr.AudioFile(chunk_path) as source:
            try:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                transcription += text.strip() + "\n\n"
            except sr.UnknownValueError:
                logging.warning(f"Could not understand chunk {i}")
            except sr.RequestError as e:
                logging.error(f"API error for chunk {i}: {e}")

    return transcription.strip()
