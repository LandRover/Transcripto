import re
import requests


def verify_response(response: requests.Response):
    try:
        response.raise_for_status()
    except requests.HTTPError:
        throw_exception(response)


def throw_exception(response: requests.Response):
    raise Exception(
        f"Request failed with error code {response.status_code}: {response.text}"
    )


import re

def is_valid_url(url):
    url_pattern = re.compile(
        r'^(https?:\/\/)'        # http:// or https://
        r'.*'                    # Match anything after https://
        r'\.mp3(\?.*)?$',        # Ensure .mp3 is in the URL, optionally followed by query parameters
        re.IGNORECASE
    )
    return re.match(url_pattern, url) is not None
