import re
from nltk.tokenize import sent_tokenize

def split_text_into_paragraphs(text, max_sentences=5):
    """
    Break a long text into paragraphs with a defined number of sentences,
    while maintaining context-aware sentence grouping.

    Args:
        text (str): The input long text in one line.
        max_sentences (int): Number of sentences per paragraph.

    Returns:
        str: Text broken into paragraphs.
    """
    # Download NLTK punkt tokenizer if not already downloaded
    import nltk
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
        nltk.download('punkt_tab')
    
    # Split text into sentences using NLTK's sentence tokenizer
    sentences = sent_tokenize(text)
    
    # Group sentences into paragraphs based on context
    paragraphs = []
    paragraph = []
    current_length = 0

    for sentence in sentences:
        paragraph.append(sentence)
        current_length += 1
        # Determine paragraph boundary based on max_sentences or sentence-ending context
        if current_length >= max_sentences or sentence.endswith(('"', "'", ':')):
            paragraphs.append(' '.join(paragraph))
            paragraph = []
            current_length = 0
    
    # Add any remaining sentences as a paragraph
    if paragraph:
        paragraphs.append(' '.join(paragraph))

    # Join paragraphs with double newlines
    return '\n\n'.join(paragraphs)


def strip_html_tags(text):
    """
    Strips all HTML tags from the given text.
    
    Args:
        text (str): The input string containing HTML tags.
        
    Returns:
        str: The text with all HTML tags removed.
    """
    if not text:
        return ""
    # Remove all HTML tags
    clean_text = re.sub(r'<[^>]+>', '', text)
    # Unescape HTML entities
    clean_text = re.sub(r'&[#\w]+;', '', clean_text)  # Removes entities like &#39; and &nbsp;
    return clean_text.strip()