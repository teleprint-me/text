"""
text_extraction/processor/html.py

Copyright (C) 2024 Austin Berrio
"""

import os
from logging import Logger
from pathlib import Path
from typing import Optional, Union

import html2text
import tqdm
from bs4 import BeautifulSoup
from markdown_it import MarkdownIt

from text_extraction.file_manager import FileManager


def clean_code_blocks(html: str) -> str:
    """Clean up 'pre' blocks by removing 'a' tags within them."""
    soup = BeautifulSoup(html, "html.parser")

    for pre_tag in soup.find_all("pre"):
        for a_tag in pre_tag.find_all("a"):
            a_tag.replace_with(a_tag.text)

    return str(soup)


def convert_html_to_markdown(html: str) -> str:
    """Convert HTML content to Markdown format."""
    h = html2text.HTML2Text()

    h.body_width = 0  # No line wrapping
    h.single_line_break = True  # Single newlines turn into <br>
    h.ignore_links = True
    h.ignore_images = True
    h.ignore_tables = True
    h.escape_all = True  # Don't escape special characters

    return h.handle(html).strip()


def replace_code_tags_with_backticks(markdown_text: str) -> str:
    """Replace custom [code] tags with Markdown code block syntax."""
    return markdown_text.replace("[code]", "```").replace("[/code]", "```")


def process_content(html_content: str) -> str:
    """Process HTML content to clean and convert to Markdown."""
    cleaned_html = clean_code_blocks(html_content)
    # NOTE: Substitute anchor paths to maintain references
    markdown_content = convert_html_to_markdown(cleaned_html).replace(".html", ".md")
    # NOTE: Replacing code tags with backticks has inconsistent side effects.
    final_content = replace_code_tags_with_backticks(markdown_content)
    return final_content


def get_output_file_path(
    input_file_path: Union[str, Path], output_dir: Union[str, Path]
) -> Path:
    """Generate the output file path with a .md extension."""
    output_file_name = Path(input_file_path).stem + ".md"
    return Path(output_dir) / output_file_name


def process_file_entry(
    file_entry: Union[str, Path, os.DirEntry],
    output_dir: Union[str, Path],
    dry_run: bool,
    logger: Logger,
    pbar: Optional[tqdm.tqdm] = None,
) -> None:
    """Process a file or directory entry and convert it from HTML to Markdown."""
    file_entry = Path(
        file_entry.path if isinstance(file_entry, os.DirEntry) else file_entry
    )
    output_dir = Path(output_dir)

    html_content = FileManager.read(file_entry)
    if html_content is None:
        logger.error(f"Failed to read {file_entry.name}. Skipping.")
        return

    markdown_content = process_content(html_content)

    if output_dir.is_file():
        raise ValueError("Expected a directory. Got a file instead.")

    output_file = get_output_file_path(file_entry, output_dir)

    if dry_run:
        logger.info(f"Would write {len(markdown_content)} bytes to {output_file}")
        return

    FileManager.write(output_file, markdown_content)

    if pbar:
        pbar.update(1)
