"""
text_extraction/processor/html.py

Copyright (C) 2024 Austin Berrio
"""

import logging
import os
import re

import html2text
import tqdm
from bs4 import BeautifulSoup
from markdown_it import MarkdownIt

from text_extraction.file_manager import FileManager
from text_extraction.logger import get_default_logger


def clean_code_blocks(html: str) -> str:
    # Initialize BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Find all 'pre' tags
    for pre_tag in soup.find_all("pre"):
        # Find all 'a' tags within each 'pre' tag
        for a_tag in pre_tag.find_all("a"):
            # Replace 'a' tag with its contents
            a_tag.replace_with(a_tag.text)

    # Convert back to string
    cleaned_html = str(soup)

    return cleaned_html


def convert_html_to_markdown(
    html: str,
) -> str:
    h = html2text.HTML2Text()
    h.body_width = 0  # No line wrapping
    h.single_line_break = True  # Single newlines turn into <br>
    h.ignore_links = True
    h.ignore_images = True
    h.ignore_tables = True
    h.escape_all = True  # Don't escape special characters

    return h.handle(html).strip()


def replace_code_tags_with_backticks(markdown_text: str) -> str:
    # Replace `[code]` with triple backticks
    markdown_text = re.sub(r"\[code\]", "```", markdown_text)
    # Replace `[/code]` with triple backticks
    markdown_text = re.sub(r"\[/code\]", "```", markdown_text)
    return markdown_text


def process_entry(file_entry: os.DirEntry, pbar: tqdm.tqdm, dry_run: bool) -> None:
    """Process a single directory entry (file) and convert it to Markdown if needed."""
    md = MarkdownIt()
    output_path = os.path.join("markdown_dataset", file_entry.path)

    html_content = FileManager.read(file_entry.path)
    if html_content is None:
        get_default_logger(__name__, logging.ERROR).error(
            f"An error occurred while reading the file {file_entry.name}. Skipping."
        )
        return

    html_content = clean_code_blocks(html_content)
    markdown_content = convert_html_to_markdown(html_content)
    markdown_content = markdown_content.replace(".html", ".md")
    output_path = output_path.replace(".html", ".md")

    if not dry_run:
        FileManager.write(output_path, markdown_content)
        pbar.update(1)
    else:
        get_default_logger(__name__, logging.INFO).info(
            f"Would write {len(markdown_content)} bytes to {output_path}"
        )
