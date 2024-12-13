
import logging
import argparse
import os
import time
import json
from dotenv import load_dotenv
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
#from src.downloader import download_mp3
#from src.transcriber import transcribe_audio
#from src.summarizer import summarize_text_with_retry
#from src.utils import validate_audio_file, cleanup_temp_files, extract_audio_metadata
from handlers.transcription_handler import process_transcription
from handlers.summarization_handler import process_summarization
from handlers.download_handler import validate_and_download
from handlers.metadata_handler import fetch_audio_metadata
from config import setup_logging, TEMP_DIR, OUTPUT_DIR
from utils.file_utils import ensure_directories, extract_filename

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Audio Transcription Script with Improvements")
    parser.add_argument("http_audio_url", type=str, help="URL or local path of the MP3 file")
    parser.add_argument("--audio-ext", type=str, default="mp3", help="Default output audio ext, usually mp3")
    parser.add_argument("--min-silence-len", type=int, default=1000, help="Minimum silence length in ms")
    parser.add_argument("--silence-thresh", type=int, default=-14, help="Silence threshold relative to dBFS")
    parser.add_argument("--temp-dir", type=str, default="/tmp", help="Directory for temporary files")
    parser.add_argument("--output-dir", type=str, default="./output", help="Directory to save output files")
    parser.add_argument("--transcript_engine", type=str, default="wisper", help="Transcription engine")
    parser.add_argument("--language", type=str, default="en-US", help="Language code for transcription")
    parser.add_argument("--force", action="store_true", help="Force recreation of output files")
    parser.add_argument("--summarize", action="store_true", help="Generate a summarized output file")
    parser.add_argument("--log-level", type=str, default="INFO", help="Set logging level (DEBUG, INFO, WARNING, ERROR)")
    args = parser.parse_args()

    setup_logging(args.log_level)
    ensure_directories([TEMP_DIR, OUTPUT_DIR])

    try:
        audio_url = validate_and_download(args.http_audio_url, args.temp_dir)
        title = extract_filename(audio_url)
        metadata = fetch_audio_metadata(audio_url)

        transcription_text = process_transcription(
            audio_url,
            args.temp_dir,
            title,
            args.audio_ext,
            args.transcript_engine,
            language=args.language,
            min_silence_len=args.min_silence_len,
            silence_thresh=args.silence_thresh,
            force=args.force
        )

        summary = None
        if args.summarize:
            summary_text = process_summarization(
                transcription_text,
                title,
                args.force
            )

        print(f"Metadata: {metadata}")
        print(f"Transcription saved. {'Summary saved.' if summary_text else ''}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
