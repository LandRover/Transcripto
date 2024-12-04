import argparse
import logging
import os
import time
from src.downloader import download_mp3
from src.transcriber import transcribe_audio
from src.summarizer import summarize_text

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

def main():
    setup_logging()

    parser = argparse.ArgumentParser(description="Audio Transcription Script")
    parser.add_argument("input", type=str, help="URL or local path of the MP3 file")
    parser.add_argument(
        "--chunk_size", type=int, default=1024, help="Chunk size for audio processing"
    )
    parser.add_argument(
        "--temp_dir", type=str, default="/tmp", help="Directory for temporary files"
    )
    parser.add_argument(
        "--language", type=str, default="en-US", help="Language code for transcription"
    )
    parser.add_argument(
        "--force", action="store_true", help="Force recreation of output files"
    )
    parser.add_argument(
        "--summarize", action="store_true", help="Generate a summarized output file"
    )
    args = parser.parse_args()

    # Ensure temp directory exists
    os.makedirs(args.temp_dir, exist_ok=True)

    # Download or verify MP3 file
    logging.info("Starting MP3 file download/check...")
    mp3_path = download_mp3(args.input, args.temp_dir)

    # Determine output file paths
    base_filename = os.path.splitext(os.path.basename(mp3_path))[0]
    raw_text_file = f"{base_filename}.txt"
    summary_file = f"{base_filename}_summary.txt"

    # Transcription step
    if not args.force and os.path.exists(raw_text_file):
        logging.info(f"Raw transcription file already exists: {raw_text_file}")
        with open(raw_text_file, "r", encoding="utf-8") as f:
            transcription = f.read()
    else:
        logging.info("Starting transcription...")
        start_transcription_time = time.time()
        transcription = transcribe_audio(
            mp3_path, args.temp_dir, language=args.language, chunk_size=args.chunk_size, force=args.force
        )
        transcription_time = time.time() - start_transcription_time
        logging.info(f"Transcription completed in {transcription_time:.2f} seconds.")

        # Save raw transcription to file
        with open(raw_text_file, "w", encoding="utf-8") as f:
            f.write(transcription)
        logging.info(f"Raw transcription saved to {raw_text_file}")

    # Summarization step (if enabled)
    if args.summarize:
        if not args.force and os.path.exists(summary_file):
            logging.info(f"Summary file already exists: {summary_file}")
        else:
            logging.info("Starting summarization...")
            start_summarization_time = time.time()
            summary = summarize_text(transcription)
            summarization_time = time.time() - start_summarization_time
            logging.info(f"Summarization completed in {summarization_time:.2f} seconds.")

            # Save summary to file
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(summary)
            logging.info(f"Summary saved to {summary_file}")

    # Process summary
    logging.info("Process Summary:")
    if args.force:
        logging.info("Force mode enabled: All output files were recreated.")
    logging.info(f"Raw transcription file: {raw_text_file}")
    if args.summarize:
        logging.info(f"Summary file: {summary_file}")
    logging.info("All tasks completed successfully.")

if __name__ == "__main__":
    main()
