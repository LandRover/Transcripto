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
