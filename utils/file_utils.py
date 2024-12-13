import os
import requests
from urllib.parse import urlparse


def ensure_directories(directories):
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def save_to_file(file_path, content):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def get_output_file(base_name, extension):
    return f"./output/{base_name}.{extension}"


def download_file(url):
    response = requests.get(url, stream=True)
    file_path = f"./temp/{os.path.basename(url)}"
    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return file_path


def extract_filename(url):
    # Parse the URL
    parsed_url = urlparse(url)

    # Extract the path and get the basename
    filename_with_ext = os.path.basename(parsed_url.path)

    # Remove the extension
    filename, _ = os.path.splitext(filename_with_ext)

    return filename

