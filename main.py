import argparse
import logging
import os
import time
from tqdm import tqdm
from dotenv import load_dotenv
from src.downloader import download_mp3
from src.transcriber import transcribe_audio
from src.summarizer import summarize_text_with_retry
from src.utils import validate_audio_file, cleanup_temp_files, extract_audio_metadata

def setup_logging(log_level):
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

def main():
    # Load environment variables
    load_dotenv()

    parser = argparse.ArgumentParser(description="Audio Transcription Script with Improvements")
    parser.add_argument("input", type=str, help="URL or local path of the MP3 file")
    parser.add_argument("--min-silence-len", type=int, default=1000, help="Minimum silence length in ms")
    parser.add_argument("--silence-thresh", type=int, default=-14, help="Silence threshold relative to dBFS")
    parser.add_argument("--temp_dir", type=str, default="/tmp", help="Directory for temporary files")
    parser.add_argument("--output_dir", type=str, default="./output", help="Directory to save output files")
    parser.add_argument("--language", type=str, default="en-US", help="Language code for transcription")
    parser.add_argument("--force", action="store_true", help="Force recreation of output files")
    parser.add_argument("--summarize", action="store_true", help="Generate a summarized output file")
    parser.add_argument("--log-level", type=str, default="INFO", help="Set logging level (DEBUG, INFO, WARNING, ERROR)")
    args = parser.parse_args()

    # Set up logging
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    setup_logging(log_level)

    # Ensure temp and output directories exist
    os.makedirs(args.temp_dir, exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)

    # Validate and download audio file
    try:
        validate_audio_file(args.input)
        logging.info("Starting MP3 file download/check...")
        mp3_path = download_mp3(args.input, args.temp_dir)
    except Exception as e:
        logging.error(f"Audio validation or download failed: {e}")
        return

    # Extract metadata
    metadata = extract_audio_metadata(mp3_path)
    logging.info(f"Audio Metadata: {metadata}")

    # Determine output file paths
    base_filename = os.path.splitext(os.path.basename(mp3_path))[0]
    raw_text_file = os.path.join(args.output_dir, f"{base_filename}.txt")
    summary_file = os.path.join(args.output_dir, f"{base_filename}_summary.txt")
    json_output_file = os.path.join(args.output_dir, f"{base_filename}.json")

    # Transcription step
    if not args.force and os.path.exists(raw_text_file):
        logging.info(f"Raw transcription file already exists: {raw_text_file}")
        with open(raw_text_file, "r", encoding="utf-8") as f:
            transcription = f.read()
    else:
        logging.info("Starting transcription...")
        start_transcription_time = time.time()
        transcription = transcribe_audio(
            mp3_path,
            args.temp_dir,
            language=args.language,
            min_silence_len=args.min_silence_len,
            silence_thresh=args.silence_thresh,
            force=args.force
        )
        transcription_time = time.time() - start_transcription_time
        logging.info(f"Transcription completed in {transcription_time:.2f} seconds.")

        # Save raw transcription to file
        with open(raw_text_file, "w", encoding="utf-8") as f:
            f.write(transcription)
        logging.info(f"Raw transcription saved to {raw_text_file}")

    # Summarization step
    summary = None
    if args.summarize:
        if not args.force and os.path.exists(summary_file):
            logging.info(f"Summary file already exists: {summary_file}")
            with open(summary_file, "r", encoding="utf-8") as f:
                summary = f.read()
        else:
            logging.info("Starting summarization...")
            start_summarization_time = time.time()
            summary = summarize_text_with_retry(transcription)
            summarization_time = time.time() - start_summarization_time
            logging.info(f"Summarization completed in {summarization_time:.2f} seconds.")

            # Save summary to file
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(summary)
            logging.info(f"Summary saved to {summary_file}")

    # Save structured JSON output
    output_data = {
        "raw_transcription": transcription,
        "summary": summary,
        "metadata": metadata,
    }
    with open(json_output_file, "w", encoding="utf-8") as json_file:
        import json
        json.dump(output_data, json_file, indent=4)
    logging.info(f"JSON output saved to {json_output_file}")

    # Cleanup temp files
    # cleanup_temp_files(args.temp_dir)
    logging.info("Temporary files cleaned up.")

    # Process summary
    logging.info("Process Summary:")
    if args.force:
        logging.info("Force mode enabled: All output files were recreated.")
    logging.info(f"Raw transcription file: {raw_text_file}")
    if args.summarize:
        logging.info(f"Summary file: {summary_file}")
    logging.info(f"JSON output file: {json_output_file}")
    logging.info("All tasks completed successfully.")

if __name__ == "__main__":
    main()
