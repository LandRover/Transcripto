import argparse
import logging
import os
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
        "--output", type=str, default="transcription_output.txt", help="Output file name"
    )
    parser.add_argument(
        "--temp_dir", type=str, default="/tmp", help="Directory for temporary files"
    )
    parser.add_argument(
        "--summarize", action="store_true", help="Summarize the transcription output"
    )
    args = parser.parse_args()

    # Ensure temp directory exists
    os.makedirs(args.temp_dir, exist_ok=True)

    # Download or verify MP3 file
    logging.info("Starting MP3 file download/check...")
    mp3_path = download_mp3(args.input, args.temp_dir)

    # Transcribe the audio
    logging.info("Starting transcription...")
    transcription = transcribe_audio(mp3_path, args.temp_dir, chunk_size=args.chunk_size)

    # Save transcription
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(transcription)
    logging.info(f"Transcription completed and saved to {args.output}")

    # Summarize the transcription if requested
    if args.summarize:
        logging.info("Summarizing transcription...")
        summary = summarize_text(transcription)
        print("\nSummary:\n", summary)

if __name__ == "__main__":
    main()
