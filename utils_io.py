#!/usr/bin/env python3
"""Utility functions for file input and output."""

from pathlib import Path


def read_text_file(file_path: str) -> str:
    """Read a file from the given path and return it as a string.

    Args:
        file_path (str): The path to the file to be read.

    Returns:
        str: The text content of the file.
    """
    return Path(file_path).read_text(encoding="utf-8")


if __name__ == "__main__":
    pass
