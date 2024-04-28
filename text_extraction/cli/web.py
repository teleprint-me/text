"""
text_extraction/processor/web.py

Copyright (C) 2024 Austin Berrio
"""

import argparse
import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Union
from urllib.parse import urlparse

import html2text
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class WebsiteCache:
    def __init__(self, cache_path: Optional[Union[str, Path]] = None):
        if cache_path is None:
            cache_path = "."
        self.path = cache_path

    @property
    def path(self) -> Path:
        return self._cache_path

    @path.setter
    def path(self, value: Union[str, Path]):
        if isinstance(value, Path):
            self._cache_path = value
        else:  # convert str to Path instance
            self._cache_path = Path(value)

    def read(self, path: Union[str, Path]) -> Optional[str]:
        try:  # if path exists
            with open(path, "r") as f:
                return f.read()
        except FileNotFoundError:
            return None  # No such path exists

    def write(self, path: str, content: str) -> None:
        # create the directory even if it exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)


class WebsiteFetcher:
    def __init__(self):
        # Configure WebDriver to run headlessly
        self.options = Options()
        # NOTE: `options.headless = True` has been deprecated and removed
        self.options.add_argument("--headless=new")

    def fetch_content(self, url: str) -> str:
        try:
            # Set up the WebDriver
            driver = webdriver.Chrome(
                options=self.options
            )  # or webdriver.Firefox() or another browser driver
            # Navigate to the webpage
            driver.get(url)
            # Retrieve the HTML content of the webpage
            html_content = driver.page_source
            return html_content
        except Exception as e:
            # Fail gracefully and return the error message as a string
            return f"Error fetching content from {url}: {str(e)}."
        finally:
            # Close the WebDriver
            driver.quit()

    def convert_html_to_markdown(
        self, html: str, settings: Optional[Dict[str, bool]] = None
    ) -> str:
        if settings is None:
            settings = {}
        h = html2text.HTML2Text()
        h.wrap_links = settings.get("wrap_links", True)
        h.single_line_break = settings.get("single_line_break", True)
        h.mark_code = settings.get("mark_code", True)
        h.wrap_list_items = settings.get("wrap_list_items", True)
        h.wrap_tables = settings.get("wrap_tables", True)
        h.re_md_chars_matcher_all = settings.get("re_md_chard_matcher_all", True)
        return h.handle(html).strip()


class WebsiteManager:
    def __init__(self, cache_path: str | Path = None):
        self.cache = WebsiteCache(cache_path)
        self.fetcher = WebsiteFetcher()

    @property
    def cache_path(self) -> Path:
        return self.cache.path

    @cache_path.setter
    def cache_path(self, value: Union[str, Path]) -> None:
        self.cache.path = value

    def get(
        self, url: str, markdown_settings: Optional[Dict[str, bool]] = None
    ) -> Tuple[str, str]:
        # Get the paths for the cache
        html_path, markdown_path = self._get_cache_paths(url)
        # Try to read from cache
        markdown_content = self.cache.read(markdown_path)
        # If the cache does not exist, fetch the HTML content
        html_content = self._fetch_html_content(html_path, url)
        # Convert HTML to markdown
        markdown_content = self.fetcher.convert_html_to_markdown(
            html_content, markdown_settings
        )
        # Cache the markdown content
        self.cache.write(markdown_path, markdown_content)
        return markdown_path, markdown_content

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


def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "url",
        type=str,
        help="The website url to download the webpage from",
    )
    parser.add_argument(
        "--cache",
        metavar="PATH",
        type=str,
        help="The cache path to write the html and markdown documents to. Default is current working directory.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Output the resulting markdown content to standard output",
    )
    parser.add_argument(
        "--wrap-links", action="store_false", help="Wrap links. Default is True."
    )
    parser.add_argument(
        "--single-line-break",
        action="store_false",
        help="Single line break. Default is True.",
    )
    parser.add_argument(
        "--mark-code", action="store_false", help="Mark code. Default is True."
    )
    parser.add_argument(
        "--wrap-list-items",
        action="store_false",
        help="Wrap list items. Default is True.",
    )
    parser.add_argument(
        "--wrap-tables", action="store_false", help="Wrap tables. Default is True."
    )
    parser.add_argument(
        "--re-md-chars-matcher-all",
        action="store_false",
        help="Pattern match all markdown characters. Default is True.",
    )
    return parser.parse_args()


def main():
    args = get_arguments()
    print(f"Attempting to get content from {args.url}")
    website_manager = WebsiteManager(args.cache)
    markdown_path, markdown_content = website_manager.get(
        args.url,
        {
            "wrap_links": args.wrap_links,
            "single_line_break": args.single_line_break,
            "mark_code": args.mark_code,
            "wrap_list_items": args.wrap_list_items,
            "wrap_tables": args.wrap_tables,
            "re_md_chars_matcher_all": args.re_md_chars_matcher_all,
        },
    )
    if args.stdout:
        print(markdown_content)
    print(f"Wrote {len(markdown_content)} bytes to {markdown_path}")


if __name__ == "__main__":
    main()
