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


def is_valid_url(url):
    # Simple regex pattern to validate a URL
    url_pattern = re.compile(
        r'^(https?:\/\/)'  # http:// or https://
        r'(([\da-z.-]+)\.([a-z.]{2,6}))'  # domain name
        r'(\/[\w\-.~:%]*)*$',  # optional path
        re.IGNORECASE
    )
    return re.match(url_pattern, url) is not None

