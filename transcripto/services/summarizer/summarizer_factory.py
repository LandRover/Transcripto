from .openai_summarizer import OpenAISummarizer


class SummarizerFactory:
    summarizers_engines_mapping = {
        "openai": OpenAISummarizer,
    }

    @staticmethod
    def get_summarizer(summarizer_engine):
        summarizer_cls = SummarizerFactory.summarizers_engines_mapping.get(summarizer_engine)
        if not summarizer_cls:
            raise ValueError(f"Unsupported summarizer engine: {summarizer_engine}")
        return summarizer_cls()

