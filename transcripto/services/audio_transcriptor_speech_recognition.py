from pydub import AudioSegment
from pydub.silence import split_on_silence
import logging
import speech_recognition as sr

import os
import logging
from tqdm import tqdm
from pydub import AudioSegment
from pydub.silence import split_on_silence
import speech_recognition as sr
from concurrent.futures import ThreadPoolExecutor


def transcribe_audio_speech_recognition(
    mp3_path, temp_dir, title, language="en-US", force=False, min_silence_len=1000, silence_thresh=-14
):
    """
    Transcribes an MP3 file into text with chunk processing, logging, and error handling.

    Args:
        mp3_path (str): Path to the MP3 file.
        temp_dir (str): Directory for temporary chunk files.
        language (str): Language code for transcription.
        min_silence_len (int): Minimum silence length to split audio (ms).
        silence_thresh (int): Silence threshold relative to dBFS.
        force (bool): Force reprocessing of existing chunks.

    Returns:
        str: Final transcription text.
    """
    # Load audio
    try:
        audio = AudioSegment.from_mp3(mp3_path)
    except Exception as e:
        logging.error(f"Failed to load audio file: {e}")
        return ""


    # Split the audio into chunks
    logging.info("Splitting audio into chunks...")
    try:
        chunks = split_on_silence(
            audio,
            min_silence_len = min_silence_len,
            silence_thresh = audio.dBFS + silence_thresh,
            keep_silence = 500,
        )
    except Exception as e:
        logging.error(f"Error splitting audio: {e}")
        return ""


    if not chunks:
        logging.error("No chunks detected. Check silence threshold and audio content.")
        return ""


    # Debug: Log chunk details
    for i, chunk in enumerate(chunks, start=1):
        logging.debug(f"Chunk {i}: Length={len(chunk)}ms, dBFS={chunk.dBFS}")

    logging.info(f"Detected {len(chunks)} chunks for transcription.")


    recognizer = sr.Recognizer()
    transcription_results = {}
    problematic_chunks = []


    def process_chunk(chunk_info):
        """
        Process a single chunk: save it as WAV, transcribe, and handle errors.
        """
        chunk_id, chunk = chunk_info
        chunk_path = os.path.join(temp_dir, f"{title}_chunk_{chunk_id}.wav")


        # Export chunk to WAV format
        try:
            # Skip export chunk if already processed, wav file exists
            if force or not os.path.exists(chunk_path):
                chunk.export(chunk_path, format="wav")
                logging.debug(f"Exported {chunk_path}: Length={len(chunk)}ms")
            else:
                logging.info(f"Skipping chunk {chunk_id}: already exists.")
        except Exception as e:
            logging.error(f"Failed to export chunk {chunk_id}: {e}")
            problematic_chunks.append(chunk_path)
            return chunk_id, ""


        # Transcribe chunk
        try:
            # Load and process the audio file
            with sr.AudioFile(chunk_path) as source:
                audio_data = recognizer.record(source) # Record the entire audio
                text = recognizer.recognize_google(audio_data, language=language)
                logging.debug(f"Chunk {chunk_path} -> Chunk_ID: {chunk_id} transcription: {text}")
                return chunk_id, text.strip()
        except sr.UnknownValueError:
            logging.warning(f"Could not understand Chunk_ID: {chunk_path} -> {chunk_id}")
            problematic_chunks.append(chunk_path)
            return chunk_id, ""
        except sr.RequestError as e:
            logging.error(f"API request error for Chunk_ID: {chunk_path} -> {chunk_id}: {e}")
            problematic_chunks.append(chunk_path)
            return chunk_id, ""


    # Process all chunks in parallel
    try:
        with ThreadPoolExecutor() as executor:
            results = list(
                tqdm(
                    executor.map(process_chunk, enumerate(chunks, start=1)),
                    total = len(chunks),
                    desc = "Processing Chunks",
                )
            )
    except Exception as e:
        logging.error(f"Error during chunk processing: {e}")
        return ""


    # Collect results explicitly to avoid losing chunks
    for chunk_id, text in results:
        if text:
            transcription_results[chunk_id] = text
        else:
            logging.warning(f"Chunk {chunk_id} returned empty transcription.")


    # Ensure transcription results are sorted by chunk ID
    sorted_results = [transcription_results[chunk_id] for chunk_id in sorted(transcription_results)]


    # Combine transcribed text
    if sorted_results:
        transcription = "\n\n".join(sorted_results)
        logging.info("Transcription successfully combined.")
    else:
        logging.warning("No transcriptions were successful. The output file will be empty.")
        transcription = ""


    # Log and save problematic chunks
    if problematic_chunks:
        problematic_file = os.path.join(temp_dir, "problematic_chunks.txt")
        with open(problematic_file, "w", encoding="utf-8") as f:
            f.writelines(f"{chunk}\n" for chunk in problematic_chunks)
        logging.warning(f"Problematic chunks saved to {problematic_file}")

    return transcription
