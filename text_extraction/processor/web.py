"""
text_extraction/processor/web.py

Copyright (C) 2024 Austin Berrio
"""

import os
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse

import html2text
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class WebsiteCache:
    def __init__(self, cache_path: Optional[Union[str, Path]] = None):
        if cache_path is None:
            cache_path = "."
        self.path = cache_path

    def read(self, endpoint: Union[str, Path]) -> Optional[str]:
        file_path = self.path + endpoint
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return f.read()
        return None  # No such content exists

    def write(self, endpoint: str, content: str) -> None:
        file_path = self.path + endpoint
        # create the directory even if it exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)


class WebsiteFetcher:
    def fetch_content(url: str) -> str:
        # Configure WebDriver to run headlessly
        options = Options()
        options.headless = True

        # Set up the WebDriver
        driver = webdriver.Chrome(
            options=options
        )  # or webdriver.Firefox() or another browser driver

        try:
            # Navigate to the webpage
            driver.get(url)
            # Retrieve the HTML content of the webpage
            html_content = driver.page_source
            return html_content
        except Exception as e:
            return f"Error fetching content from {url}: {str(e)}."
        finally:
            # Close the WebDriver
            driver.quit()

    def convert_html_to_markdown(html: str) -> str:
        h = html2text.HTML2Text()
        h.wrap_links = True
        h.single_line_break = True
        h.mark_code = True
        h.wrap_list_items = True
        h.wrap_tables = True
        h.re_md_chars_matcher_all = True
        return h.handle(html).strip()


class WebsiteManager:
    def __init__(self, cache_path: str | Path = None):
        self.cache = WebsiteCache(cache_path)
        self.fetcher = WebsiteFetcher()

    @property
    def cache_path(self) -> str:
        return self.fetcher.cache_path

    @cache_path.setter
    def cache_path(self, value: str) -> None:
        self.website_fetcher.cache_path = value

    def get(self, url: str) -> str:
        # Get the paths for the cache
        html_path, markdown_path = self._get_cache_paths(url)

        # Try to read from cache
        markdown_content = self.cache.read(markdown_path)
        if markdown_content is not None:
            return self.queue_proxy.handle_content_size(markdown_content, markdown_path)

        # If the cache does not exist, fetch the HTML content
        html_content = self._fetch_html_content(html_path, url)
        # Convert HTML to markdown
        markdown_content = self.fetcher.convert_html_to_markdown(html_content)
        # Cache the markdown content
        self.cache.write(markdown_path, markdown_content)

        return self.queue_proxy.handle_content_size(markdown_content, markdown_path)

    def _get_cache_paths(self, url: str) -> tuple[str, str]:
        # Create paths for the cache
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        # Remove leading slash
        # If path is empty, use 'index' as the default filename
        path = parsed_url.path.lstrip("/") or "index.html"
        html_path = os.path.join(self.cache.path, "html", domain, path)

        markdown_path = os.path.join(
            self.cache.path,
            "markdown",
            domain,
            f"{os.path.splitext(path)[0]}.md",
        )

        return html_path, markdown_path

    def _fetch_html_content(self, html_path: str, url: str) -> str:
        html_content = self.cache.read(html_path)
        if html_content is None:
            html_content = self.fetcher.fetch_content(url)
            # Cache the HTML content
            self.cache.write(html_path, html_content)

        return html_content
