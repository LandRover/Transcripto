import os
import time
import logging
from openai import OpenAI
from .summarizer_base import SummarizerBase

class OpenAISummarizer(SummarizerBase):

    def get_guidelines_for_prompt_full_summary(self):
        guidelines = [
            {
                "title": "Detail and Depth",
                "focuses": [
                    "The summary must be detailed and thorough yet concise, capturing the essence of the original text with precision.",
                    "Include critical insights and key takeaways without oversimplifying or losing nuance."
                ]
            },
            {
                "title": "Chronological Flow",
                "focuses": [
                    "Maintain the chronological order of ideas and events as presented in the text.",
                    "Ensure the summary reflects the sequence of topics and themes accurately."
                ]
            },
            {
                "title": "Strict Text Reliance",
                "focuses": [
                    "Use only the information available in the provided text.",
                    "Avoid introducing external knowledge or assumptions."
                ]
            },
            {
                "title": "Actionable Insights",
                "focuses": [
                    "Focus on answering the question: 'What's in it for me?' for the listener.",
                    "Highlight lessons, practical takeaways, and actionable ideas the listener will gain from the content."
                ]
            },
            {
                "title": "Structured Format",
                "focuses": [
                    "Present the summary as 6 key points, each with 4 sub-points providing additional depth and clarity.",
                    "Use bullet points for easy readability and logical organization."
                ]
            },
            {
                "title": "Language Alignment",
                "focuses": [
                    "Respond in the same language, Hebrew, as the input text to preserve its original tone and context.",
                    "Ensure that the language and style align with the input text accurately and naturally."
                ]
            }
        ]

        prompt = "As a professional summarizer, generate a structured and comprehensive summary of the provided text, ensuring it adheres to the following guidelines:\n"

        for guideline in guidelines:
            prompt += f"{guideline['title']}:\n"
            for focuse in guideline["focuses"]:
                prompt += f"  * {focuse}\n"

        return prompt


    def summarize_text(self, text, model="gpt-4o-mini", max_tokens=1024, temperature=0.1, retries=3, delay=2):
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

                guidelines = self.get_guidelines_for_prompt_full_summary()
                prompt = (f"{guidelines}"
                            "\nText to to summerize:"
                            "\n" + text)
                
                response = client.chat.completions.create(
                    model = model,
                    max_tokens = max_tokens,
                    temperature = temperature,
                    messages = [
                        {"role": "system", "content": "You're a professional text summarizer."},
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
