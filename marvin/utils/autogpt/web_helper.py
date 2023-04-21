"""Browse a webpage and summarize it using the LLM model"""
from __future__ import annotations

from urllib.parse import urljoin, urlparse

import requests
import re
from bs4 import BeautifulSoup
from requests import Response
from requests.compat import urljoin

class WebHelper:
    
    def __init__(self):
        self.session = requests.Session()

    def is_valid_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False


    def sanitize_url(self, url):
        return urljoin(url, urlparse(url).path)


    def check_local_file_access(self, url):
        local_prefixes = [
            "file:///",
            "file://localhost/",
            "file://localhost",
            "http://localhost",
            "http://localhost/",
            "https://localhost",
            "https://localhost/",
            "http://2130706433",
            "http://2130706433/",
            "https://2130706433",
            "https://2130706433/",
            "http://127.0.0.1/",
            "http://127.0.0.1",
            "https://127.0.0.1/",
            "https://127.0.0.1",
            "https://0.0.0.0/",
            "https://0.0.0.0",
            "http://0.0.0.0/",
            "http://0.0.0.0",
            "http://0000",
            "http://0000/",
            "https://0000",
            "https://0000/",
        ]
        return any(url.startswith(prefix) for prefix in local_prefixes)


    def get_response(self, url, timeout = 10):
        # Get the response from a URL
        try:
            # Restrict access to local files
            if self.check_local_file_access(url):
                return None, "Access to local files is restricted"

            # Most basic check if the URL is valid:
            if not url.startswith("http://") and not url.startswith("https://"):
                return None, "Invalid URL format"

            sanitized_url = self.sanitize_url(url)

            response = self.session.get(sanitized_url, timeout=timeout)

            # Check if the response contains an HTTP error
            if response.status_code >= 400:
                return None, f"Error: HTTP {str(response.status_code)} error"

            return response, None
        except ValueError as ve:
            # Handle invalid URL format
            return None, f"Error: {str(ve)}"

        except requests.exceptions.RequestException as re:
            # Handle exceptions related to the HTTP request
            #  (e.g., connection errors, timeouts, etc.)
            return None, f"Error: {str(re)}"


    def scrape_text(self, url):
        """Scrape text from a webpage

        Args:
            url (str): The URL to scrape text from

        Returns:
            str: The scraped text
        """
        response, error_message = self.get_response(url)
        if error_message or not response:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        for script in soup(['script', 'style']):
            script.extract()

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split('  '))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text

    def extract_url_data_from_text(self, message) -> str:
        """Extract URLs and data from text

        Returns:
            str: The extracted data from URLs
        """
        urls = re.findall(
            r'<(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)>',
            message,
        )
        if not urls:
            return None
        data_messages = []
        for url in urls:
            data = None
            if self.is_valid_url(url):
                data = self.scrape_text(url)
                data_messages.append({
                    "url": url,
                    "text": data,
                    "prompt": self.create_message(url, data),
                })

        # remove any dict with None values in "text" key
        data_messages = [d for d in data_messages if d.get("text")]
        return data_messages

    def create_message(self, url, data):
        """Create a message for the user to summarize a chunk of text"""
        return {
            "role": "user",
            "content": f'[WEB BROWSER]: The scraped data from the url "{url}" is the following """{data}"""'
            "Refer the above text as a replacement for the URL in the original message."
        }
