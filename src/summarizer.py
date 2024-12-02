import logging
import openai  # Requires the OpenAI Python SDK

def summarize_text(text):
    """Summarizes the given text using ChatGPT."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Replace with the model you prefer
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Summarize the following text:\n{text}"}
            ],
        )
        summary = response['choices'][0]['message']['content']
        return summary.strip()
    except Exception as e:
        logging.error(f"Error during summarization: {e}")
        return "Summarization failed. Check logs for details."
