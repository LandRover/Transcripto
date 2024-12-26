import os
import logging
import requests
from urllib.parse import urlparse


def ensure_directories(directories):
    for directory in directories:
        os.makedirs(directory, exist_ok=True)



def save_to_file(file_path, content):
    """
    Saves content to a file, either as text or binary, with detailed logging.

    Args:
        file_path (str): The path to the file where content will be saved.
        content (str or bytes): The content to save.

    Raises:
        TypeError: If content is not of type 'str' or 'bytes'.
    """
    try:
        logging.debug(f"Attempting to save content to {file_path}")
        
        if isinstance(content, bytes):
            logging.debug("Content is of type bytes. Opening file in binary mode.")
            with open(file_path, "wb") as f:
                f.write(content)
        elif isinstance(content, str):
            logging.debug("Content is of type str. Opening file in text mode.")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            logging.error("Invalid content type provided.")
            raise TypeError("Content must be of type 'str' or 'bytes'")
        
        logging.info(f"Successfully saved content to {file_path}")
    except IOError as ioe:
        logging.error(f"IOError encountered: {ioe}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise



def get_output_file(base_name, extension):
    return f"./output/{base_name}.{extension}"


def extract_filename_from_url(url):
    # Parse the URL
    parsed_url = urlparse(url)

    # Extract the path and get the basename
    filename_with_ext = os.path.basename(parsed_url.path)

    # Remove the extension
    filename, _ = os.path.splitext(filename_with_ext)

    return filename

