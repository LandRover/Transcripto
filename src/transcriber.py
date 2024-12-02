import os
import logging
from pydub import AudioSegment
from pydub.silence import split_on_silence
import speech_recognition as sr

def transcribe_audio(mp3_path, temp_dir, language="en-US", chunk_size=1024, force=False):
    """
    Transcribes an MP3 file into text with progress tracking, filenames including original file name and language,
    and optional skipping of already processed chunks.

    Args:
        mp3_path (str): Path to the MP3 file.
        temp_dir (str): Directory to store temporary chunk files.
        language (str): Language code for transcription (e.g., 'he-IL' for Hebrew).
        chunk_size (int): Not currently used but reserved for future audio handling configurations.
        force (bool): If True, reprocess all chunks even if transcription files exist.
    """
    audio = AudioSegment.from_mp3(mp3_path)
    total_duration = len(audio)  # Total duration in milliseconds
    original_filename = os.path.splitext(os.path.basename(mp3_path))[0]  # Extract base name without extension
    language_code = language.replace("-", "_")  # Replace hyphen for file naming compatibility

    # Split the audio into chunks based on silence
    logging.info("Splitting audio into chunks...")
    logging.info(f"Loading file {original_filename} to memory...")
    chunks = split_on_silence(
        audio,
        min_silence_len=1000,            # Minimum silence length in ms
        silence_thresh=audio.dBFS - 14,  # Silence threshold
        keep_silence=500                 # Keep some silence
    )
    logging.info(f"Audio split into {len(chunks)} chunks.")

    recognizer = sr.Recognizer()
    transcription = ""

    for i, chunk in enumerate(chunks):
        chunk_id = i + 1
        # Calculate progress as a percentage
        processed_duration = sum(len(c) for c in chunks[:i])  # Sum of processed chunks
        progress = (processed_duration / total_duration) * 100

        # Define paths for chunk file and transcription cache
        chunk_path = os.path.join(temp_dir, f"{original_filename}_{language_code}_chunk_{chunk_id}.wav")
        chunk_transcription_path = os.path.join(temp_dir, f"{original_filename}_{language_code}_chunk_{chunk_id}.txt")

        # Check if transcription for this chunk already exists
        if not force and os.path.exists(chunk_transcription_path):
            logging.info(f"Skipping chunk {chunk_id}/{len(chunks)} ({progress:.2f}% complete) - already transcribed.")
            with open(chunk_transcription_path, "r", encoding="utf-8") as f:
                transcription += f.read().strip() + "\n\n"
            continue

        # Log progress
        logging.info(f"Processing chunk {chunk_id}/{len(chunks)} ({progress:.2f}% complete)")

        # Export chunk to WAV format
        chunk.export(chunk_path, format="wav")

        # Transcribe the chunk
        with sr.AudioFile(chunk_path) as source:
            try:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data, language=language)
                transcription += text.strip() + "\n\n"

                # Save chunk transcription to file
                with open(chunk_transcription_path, "w", encoding="utf-8") as f:
                    f.write(text.strip())
            except sr.UnknownValueError:
                logging.warning(f"Could not understand chunk {chunk_id}")
            except sr.RequestError as e:
                logging.error(f"API error for chunk {chunk_id}: {e}")

    # Log final progress
    logging.info("Transcription completed.")
    return transcription.strip()
