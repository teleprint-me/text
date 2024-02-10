"""
text_extraction/cli/html.py

A Python script for converting HTML files to Markdown format.

This script recursively processes files in the input directory, converting HTML documents to Markdown format. It employs BeautifulSoup and html2text libraries to clean HTML content and perform the conversion. The script also provides detailed logging for error handling during file operations.

Copyright (C) 2024 Austin Berrio
"""

import argparse
import logging
import os
from pathlib import Path

from text_extraction.logger import get_default_logger
from text_extraction.processor.html import (
    process_html_directory,
    process_html_file_entry,
)


def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert HTML files to Markdown format."
    )
    parser.add_argument(
        "-i",
        "--input-path",
        required=True,
        default="",
        help="Path to the file or directory to process.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="converted_md",
        help="Directory to the processed output.",
    )
    parser.add_argument(
        "-t",
        "--n-threads",
        type=int,
        default=os.cpu_count() or 4,
        help="Number of threads to use for processing.",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        default=False,
        action="store_true",
        help="Perform a dry run and fake generating the C and C++ raw dataset.",
    )
    return parser.parse_args()


def main(args: argparse.Namespace):
    input_path = Path(args.input_path)
    output_path = Path(args.output_dir)
    n_threads = args.n_threads
    dry_run = args.dry_run
    logger = get_default_logger(__name__, logging.INFO)

    if input_path.is_file():
        process_html_file_entry(
            file_entry=input_path,
            output_dir=output_path,
            dry_run=dry_run,
            logger=logger,
        )
    elif input_path.is_dir():
        process_html_directory(
            input_dir=input_path,
            output_dir=output_path,
            n_threads=n_threads,
            dry_run=dry_run,
            logger=logger,
        )
    else:
        logger.error(f"Invalid input path: {input_path}. Exiting.")


if __name__ == "__main__":
    args = get_arguments()
    main(args)
