import os
import time
import logging
from openai import OpenAI



def summarize_text_with_retry(text, model="gpt-4o-mini", max_tokens=1024, temperature=0.1, retries=3, delay=2):
    """
    Summarizes the given text using OpenAI's GPT model with a focus on software R&D.

    Args:
        text (str): The text to summarize.

    Returns:
        str: The summary of the input text in 6 points.
    """

    for attempt in range(retries):
        try:
            client = OpenAI(
                api_key = os.environ.get("OPENAI_API_KEY"),
            )

            prompt = (f"I am a development manager developing software."
                        "\nThe attached text is a transcript of a podcast episode."
                        "\nHelp me summerize 6 points and 4 internal bullets in each of the essentials."
                        "\nPlease keep the chronological order of the points as they apear in the original text."
                        "\nFocus on takeaways I could use in my organiation to improve my teams."
                        "\nBe detailed, explicit and clear in the internal bullet points, not to general as it tends to be."
                        "\nRespond in Hebrew."
                        "\n\nHere is the text to to summerize:"
                        "\n" + text)

            response = client.chat.completions.create(
                model = model,
                max_tokens = max_tokens,
                temperature = temperature,
                messages = [
                    {"role": "system", "content": "You are a technical expert specializing in mostly in backend development."},
                    {"role": "user", "content": (
                        prompt
                    )}
                ]
            )
            
            # Accessing the first message's content in the response
            logging.info(response)
            logging.info(response.model_dump())
            summary = response.choices[0].message.content
            logging.info(summary)
            return summary.strip()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay * (2 ** attempt))
            else:
                logging.error(f"Summarization failed after {retries} attempts: {e}")
                return "Summarization failed."
