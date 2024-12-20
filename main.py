
import logging
import argparse
from dotenv import load_dotenv
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from transcripto.handlers.tts_handler import process_tts
from transcripto.handlers.transcription_handler import process_transcription
from transcripto.handlers.summarization_handler import process_summarization
from transcripto.handlers.download_handler import process_download
from transcripto.handlers.metadata_handler import fetch_audio_metadata
from config import setup_logging, TEMP_DIR, OUTPUT_DIR
from transcripto.utils.file_utils import ensure_directories, extract_filename

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Audio Transcription Script with Improvements")
    parser.add_argument("http_audio_url", type=str, help="URL or local path of the MP3 file")
    parser.add_argument("--audio-ext", type=str, default="mp3", help="Default output audio ext, usually mp3")
    parser.add_argument("--temp-dir", type=str, default=TEMP_DIR, help="Directory for temporary files")
    parser.add_argument("--output-dir", type=str, default=OUTPUT_DIR, help="Directory to save output files")
    parser.add_argument("--transcript_engine", type=str, default="wisper", help="Transcription model")
    parser.add_argument("--summarization_engine", type=str, default="openai", help="summarization engine")
    parser.add_argument("--summarization_model", type=str, default="gpt-4o-mini", help="summarization model")
    parser.add_argument("--tts_engine", type=str, default="openai_gpt", help="text-to-speech engine")
    parser.add_argument("--tts_model", type=str, default="gpt-4o-audio-preview", help="text-to-speech model")
    parser.add_argument("--language", type=str, default="en-US", help="Language code for transcription")
    parser.add_argument("--force", action="store_true", help="Force recreation of output files")
    parser.add_argument("--summarize", action="store_true", help="Generate a summarized output file")
    parser.add_argument("--tts", action="store_true", help="Generate a text-to-speech output file")
    parser.add_argument("--log-level", type=str, default="INFO", help="Set logging level (DEBUG, INFO, WARNING, ERROR)")
    args = parser.parse_args()

    setup_logging(args.log_level)
    ensure_directories([TEMP_DIR, OUTPUT_DIR])

    try:
        title = extract_filename(args.http_audio_url)
        audio_url = process_download(args.http_audio_url, title)

        metadata = fetch_audio_metadata(audio_url)
        logging.info(f"Metadata extracted from {audio_url}: {metadata}")

        transcription_text = process_transcription(
            audio_url,
            args.temp_dir,
            title,
            args.audio_ext,
            args.transcript_engine,
            language=args.language,
            force=args.force
        )

        summary = None
        if args.summarize:
            summary_text = process_summarization(
                transcription_text,
                title,
                args.summarization_engine,
                args.summarization_model,
                args.force
            )

        tts = None
        if args.tts and args.summarize:
            tts = process_tts(
                title,
                summary_text,
                args.tts_engine,
                args.tts_model,
                args.force,
            )
        print(f"Transcription completed. {'Summary saved.' if summary_text else ''}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
