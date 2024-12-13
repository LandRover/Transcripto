import os
import logging

TEMP_DIR = "/tmp"
OUTPUT_DIR = "./output"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"

def setup_logging(level):
    logging.basicConfig(level=level, format=LOG_FORMAT)
