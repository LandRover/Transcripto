from abc import ABC, abstractmethod

class SummarizerBase(ABC):
    @abstractmethod
    def summarize_text(self, text, model, max_tokens, temperature, retries, delay):
        pass
