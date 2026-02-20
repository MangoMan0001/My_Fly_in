#!/usr/bin/env python3

import argparse
from utils_io import read_text_file
from parsers import DroneNetworkParser

def get_args() -> argparse.Namespace:
    """コマンドライン引数の定義と取得"""
    parser = argparse.ArgumentParser(description="ドローンネットワークのシミュレーション")
    parser.add_argument("input_file", type=str, help="入力ファイルのパス")
    return parser.parse_args()

def main() -> None:
    """エントリーポイント"""
    args = get_args()

    text_data = read_text_file(args.input_file)

    parser = DroneNetworkParser()
    network = parser.parse(text_data)

    print(f"解析成功！ ドローン数: {network.nb_drones}")

if __name__ == "__main__":
    main()
