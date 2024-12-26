import os
import time
import logging
from transcripto.services.summarizer.summarizer_factory import SummarizerFactory
from transcripto.utils.file_utils import save_to_file, get_output_file

def sanitize_text(text: str) -> str:
        """
        Sanitize the given text by replacing '**' with '*' and '--' with '-'.

        Args:
            text (str): The input text to sanitize.

        Returns:
            str: The sanitized text.
        """
        sanitized_text = text.replace('**', '*').replace('--', '-')
    
        return sanitized_text

def process_summarization(text, title, summarizer_engine="openai", summarizer_model="gpt-4o-mini", force=False):
    logging.info(f"Starting summarization {title} using {summarizer_engine}...")
    start_time = time.time()

    base_filename = f"{title}_{summarizer_engine}_{summarizer_model}_summary"
    output_file = get_output_file(base_filename, "txt")

    if not force and os.path.exists(output_file):
        logging.info(f"Using existing summary: {output_file}")
        with open(output_file, "r", encoding="utf-8") as f:
            return f.read()

    # Select the transcriptor strategy
    summarizer = SummarizerFactory.get_summarizer(summarizer_engine)
    summary_output_text = sanitize_text(summarizer.summarize_text(
        text,
        summarizer_model,
        max_tokens = 1024,
        temperature = 0.1,
        retries = 3,
        delay = 2
    ))
    
    logging.info(f"Summarization completed in {time.time() - start_time:.2f} seconds.")
    save_to_file(output_file, summary_output_text)
    logging.info(f"Summary saved to {output_file}")

    return summary_output_text
