import os
import time
import logging
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from .summarizer_base import SummarizerBase


class VertexSummarizer(SummarizerBase):
    """
    Summarizer using Google Gemini models with API key authentication.
    
    Required environment variables:
        - GOOGLE_API_KEY: Your Google AI API key (from https://aistudio.google.com/apikey)
    """

    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required for Gemini")
        
        if not self.api_key.startswith("AIza"):
            logging.warning(
                "GOOGLE_API_KEY doesn't look like a valid Google AI API key. "
                "Keys should start with 'AIza...'. Get one from https://aistudio.google.com/apikey"
            )
        
        # Configure with API key only - explicitly avoid any GCP project settings
        genai.configure(api_key=self.api_key)

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
            for focus in guideline["focuses"]:
                prompt += f"  * {focus}\n"

        return prompt

    def summarize_text(self, text, model="gemini-3-pro-preview", max_tokens=1024, temperature=0.1, retries=3, delay=2):
        """
        Summarizes the given text using Google's Gemini model.

        Args:
            text (str): The text to summarize.
            model (str): The Gemini model to use (e.g., 'gemini-3-pro-preview', 'gemini-1.5-pro').
            max_tokens (int): Maximum tokens in the response.
            temperature (float): Sampling temperature.
            retries (int): Number of retry attempts.
            delay (int): Base delay between retries in seconds.

        Returns:
            str: The summary of the input text in 6 points.
        """

        # Configure safety settings to be permissive for summarization tasks
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

        for attempt in range(retries):
            try:
                generative_model = genai.GenerativeModel(
                    model_name=model,
                    system_instruction="You're a professional text summarizer.",
                    safety_settings=safety_settings
                )

                guidelines = self.get_guidelines_for_prompt_full_summary()
                prompt = (f"{guidelines}"
                          "\nText to summarize:"
                          "\n" + text)

                generation_config = genai.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                )

                response = generative_model.generate_content(
                    prompt,
                    generation_config=generation_config
                )

                # Check if response was blocked
                if not response.candidates:
                    raise ValueError("Response was blocked - no candidates returned")
                
                candidate = response.candidates[0]
                if candidate.finish_reason.name == "SAFETY":
                    raise ValueError(f"Response blocked by safety filters: {candidate.safety_ratings}")
                
                if not candidate.content.parts:
                    raise ValueError(f"No content parts in response. Finish reason: {candidate.finish_reason.name}")

                summary = candidate.content.parts[0].text
                return summary.strip()

            except Exception as e:
                if attempt < retries - 1:
                    logging.warning(f"Gemini summarization attempt {attempt + 1} failed: {e}")
                    time.sleep(delay * (2 ** attempt))
                else:
                    logging.error(f"Summarization failed after {retries} attempts: {e}")
                    return "Summarization failed."
