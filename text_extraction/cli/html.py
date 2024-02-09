"""
text_extraction/cli/html.py

A Python script for converting HTML files to Markdown format.

This script recursively processes files in the input directory, converting HTML documents to Markdown format. It employs BeautifulSoup and html2text libraries to clean HTML content and perform the conversion. The script also provides detailed logging for error handling during file operations.

Copyright (C) 2024 Austin Berrio
"""

import argparse
import logging
import os
import time

from byte_pair.processor.html import collect_files, traverse_directory

# Initialize logging
logging.basicConfig(level=logging.INFO)


def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert HTML files to Markdown format."
    )
    parser.add_argument(
        "-p",
        "--dir-path",
        required=True,
        default="",
        help="Path to the directory to process.",
    )
    parser.add_argument(
        "-t",
        "--n-threads",
        default=os.cpu_count() or 4,
        help="Number of threads to use for processing.",
    )
    parser.add_argument(
        "-r",
        "--dry-run",
        action="store_true",
        default=False,
        help="Perform a dry run and fake generating the C and C++ raw dataset.",
    )
    return parser.parse_args()


def main(args: argparse.Namespace):
    logging.info("Starting main function.")
    start_time = time.time()
    file_entry_list = collect_files(args.dir_path)
    traverse_directory(file_entry_list, args.n_threads, args.dry_run)
    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info(f"Elapsed {elapsed_time:.2f} seconds using {args.n_threads} threads.")


if __name__ == "__main__":
    args = get_arguments()
    main(args)
