import os
import logging

def ensure_directory(path):
    """Ensures a directory exists."""
    if not os.path.exists(path):
        os.makedirs(path)
        logging.info(f"Created directory: {path}")
    else:
        logging.info(f"Directory already exists: {path}")
