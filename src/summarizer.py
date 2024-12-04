import os
import logging
from openai import OpenAI

GPT_MODEL = "gpt-4o"

def summarize_text(text):
    """
    Summarizes the given text using OpenAI's GPT model with a focus on software R&D.

    Args:
        text (str): The text to summarize.

    Returns:
        str: The summary of the input text in 6 points.
    """
    try:
        client = OpenAI(
            api_key = os.environ.get("OPENAI_API_KEY"),
        )

        prompt = (f"I am a development manager,"
                    "\nThe attached text is a transcript of a podcast episode."
                    "\nHelp me summerize 5-6 points and 3 internal bullets in each of the essentials."
                    "\nFocus on takeaways I could use in my organiation to improve my teams."
                    "\nBe detailed, explicit and clear in the internal 3 bullet points."
                    "\nResponse should be in Hebrew."
                    "\n\nHere is the text to to summerize:"
                    "\n" + text)

        response = client.chat.completions.create(
            model = GPT_MODEL,
            max_tokens = 1024,
            temperature = 0.5,
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
    except openai.APIConnectionError as e:
        logging.error("The server could not be reached")
        logging.error(e.__cause__)  # an underlying Exception, likely raised within httpx.
        return "Summarization failed. Check logs for details."
    except openai.RateLimitError as e:
        logging.error("A 429 status code was received; we should back off a bit.")
        return "Summarization failed. Check logs for details."
    except openai.APIStatusError as e:
        logging.error("Another non-200-range status code was received")
        logging.error(e.status_code)
        logging.error(e.response)
        return "Summarization failed. Check logs for details."
    except openai.error.OpenAIError as e:
        logging.error(f"Error during summarization: {e}")
        return "Summarization failed. Check logs for details."
