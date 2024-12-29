import logging
import argparse
import os
from dotenv import load_dotenv
from transcripto.handlers.tts_handler import process_tts
from transcripto.handlers.transcription_handler import process_transcription
from transcripto.handlers.summarization_handler import process_summarization
from transcripto.handlers.download_handler import process_download
from config import setup_logging, TEMP_DIR, OUTPUT_DIR
from transcripto.utils.file_utils import ensure_directories
from .telegram_bot import start_loop_bot
import asyncio


def cli_mode():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Audio Transcription Script with Improvements")
    parser.add_argument("--url", type=str, default="", help="URL or local path of the MP3 file")
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
    parser.add_argument("--telegram-bot", action="store_true", help="Run as telegram bot")
    parser.add_argument("--log-level", type=str, default="INFO", help="Set logging level (DEBUG, INFO, WARNING, ERROR)")
    args = parser.parse_args()

    setup_logging(args.log_level)
    ensure_directories([TEMP_DIR, OUTPUT_DIR])

    try:
        if args.telegram_bot:
            logging.info(f"Running in Telegram bot mode.")
            TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

            try:
                asyncio.run(start_loop_bot(TELEGRAM_BOT_TOKEN))
            except RuntimeError:
                import nest_asyncio
                nest_asyncio.apply()
                asyncio.run(start_loop_bot(TELEGRAM_BOT_TOKEN))
            return

        file_title, audio_local_path, audio_metadata = process_download(args.url)
        logging.info(f"Metadata extracted from {audio_local_path}: {audio_metadata}")

        transcription_text = process_transcription(
            audio_local_path,
            args.temp_dir,
            file_title,
            args.audio_ext,
            args.transcript_engine,
            language=args.language,
            force=args.force
        )

        summary = None
        if args.summarize:
            summary_text = process_summarization(
                transcription_text,
                file_title,
                args.summarization_engine,
                args.summarization_model,
                args.force
            )

        tts = None
        if args.tts and args.summarize:
            tts = process_tts(
                file_title,
                summary_text,
                args.tts_engine,
                args.tts_model,
                args.force,
            )
        logging.info(f"Transcription completed. {'Summary saved.' if summary_text else ''}")

    except Exception as e:
        logging.error(f"Error: {e}")

