import os
import logging


OUTPUT_DIR = "./output"
TEMP_DIR = "./output/tmp"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"

def setup_logging(level):
    logging.basicConfig(level=level, format=LOG_FORMAT)
