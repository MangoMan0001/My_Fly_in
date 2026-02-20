#!/usr/bin/env python3

from pathlib import Path

def read_text_file(file_path: str) -> str:
    """
    指定されたパスのファイルを読み込み、文字列として返す。
    """

    return Path(file_path).read_text(encoding="utf-8")

if __name__ == "__main__":
    pass
