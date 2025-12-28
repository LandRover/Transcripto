import re
import logging
import requests
from .download_base import DownloadBase
from transcripto.utils.file import extract_filename_from_url
from pathlib import Path
from urllib.parse import urlparse
from config import DOAMINS_TEXT_SELECTORS

class TextDownload(DownloadBase):
    TEXT_SUPPORTED_DOMAINS = '|'.join(map(re.escape, DOAMINS_TEXT_SELECTORS.keys()))
    DEFAULT_USER_AGENT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html) Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/131.0.0.0 Safari/537.36 Googlebot/2.1 (+http://www.google.com/bot.html)"
    DEFAULT_REFERER = "https://google.com"

    def __init__(self):
        self.__apply_requests_session()


    def __apply_requests_session(self):
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "*/*",
            "accept-language": "en-US",
            "referer": self.DEFAULT_REFERER,
            "user-agent": self.DEFAULT_USER_AGENT,
        })


    def __apply_http_properties(self, referer: str, user_agent: str):
        self.session.headers.update({
            "referer": referer,
            "user-agent": user_agent,
        })
    

    def get_episode_id(self, url):
        episode_id = extract_filename_from_url(url)

        return episode_id


    def download(self, url: str, temp_path: Path):
        logging.info(f"TextDownload Starting download {url}...")

        try:
            url_data = self.parse_url(url)
            domain = url_data["domain"]
            config = self.get_config(domain)
            referer = config.get("properties", {}).get("http", {}).get("referer", self.DEFAULT_REFERER) or self.DEFAULT_REFERER
            user_agent = config.get("properties", {}).get("http", {}).get("user_agent", self.DEFAULT_USER_AGENT) or self.DEFAULT_USER_AGENT
            print(referer)
            print(user_agent)
            self.__apply_http_properties(referer, user_agent)
            response = self.session.get(url, stream = True)
            response.raise_for_status()
            logging.info(f"Download completed: {url}")

            return response.content

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return None


    def get_config(self, domain: str):
        return DOAMINS_TEXT_SELECTORS[domain]
    

    def parse_url(self, url: str):
        """
        Extract components from a URL.

        Args:
            url (str): The URL to extract components from.

        Returns:
            dict: A dictionary containing URL components.
        """
        parsed_url = urlparse(url)
        
        # Extract parts
        scheme = parsed_url.scheme
        hostname = parsed_url.hostname
        path = parsed_url.path
        query = parsed_url.query
        fragment = parsed_url.fragment

        # Parse domain and subdomain
        if hostname:
            domain_parts = hostname.split('.')
            # Handle multi-level TLDs like '.co.il'
            if len(domain_parts) >= 3 and domain_parts[-2] in ["co", "com", "org"]:
                domain = '.'.join(domain_parts[-3:])  # e.g., 'ynet.co.il'
                subdomain = '.'.join(domain_parts[:-3]) if len(domain_parts) > 3 else None
            else:
                domain = '.'.join(domain_parts[-2:])  # e.g., 'nytimes.com'
                subdomain = '.'.join(domain_parts[:-2]) if len(domain_parts) > 2 else None
        else:
            domain = subdomain = None

        # Parse path parts
        path_parts = path.strip('/').split('/') if path else []

        return {
            "scheme": scheme,
            "hostname": hostname,
            "domain": domain,
            "subdomain": subdomain,
            "path": path,
            "path_parts": path_parts,
            "query": query,
            "fragment": fragment
        }
