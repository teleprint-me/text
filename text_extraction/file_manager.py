"""
text_extraction/file_manager.py

Copyright (C) 2024 Austin Berrio
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List, Optional, Union

import tqdm

from text_extraction.logger import get_default_logger


class FileManager:
    def __init__(self, logger: Optional[logging.Logger] = None):
        if logger:
            self.logger = logger
        else:
            self.logger = get_default_logger(self.__class__.__name__, logging.INFO)

    def read(self, file_path: str) -> Optional[str]:
        """Read content from a source file."""
        try:
            with open(file_path, "r") as f:
                return f.read()
        except Exception as e:
            self.logging.error(
                f"An error occurred while reading from the source file: {e}"
            )
        return None

    def write(self, file_path: str, content: str) -> None:
        """Write content to a destination file."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                f.write(content)
        except Exception as e:
            self.logging.error(
                f"An error occurred while writing to the destination file: {e}"
            )

    @staticmethod
    def collect_files(dir_entry: Union[str, os.DirEntry]) -> List[os.DirEntry]:
        """Collect all file entries in a directory recursively."""
        file_entry_list = []
        dir_entry_path = (
            dir_entry.path if isinstance(dir_entry, os.DirEntry) else dir_entry
        )
        for entry in os.scandir(dir_entry_path):
            if entry.is_file():
                file_entry_list.append(entry)
            elif entry.is_dir():
                file_entry_list.extend(FileManager.collect_files(entry))
        return file_entry_list

    @staticmethod
    def traverse_directory(
        file_entry_list: List[os.DirEntry],
        process_entry: Callable[[os.DirEntry, tqdm.tqdm, bool], None],
        n_threads: int,
        dry_run: bool,
    ) -> None:
        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            with tqdm.tqdm(total=len(file_entry_list)) as pbar:
                for _ in executor.map(
                    lambda file_entry: process_entry(file_entry, pbar, dry_run),
                    file_entry_list,
                ):
                    pass
