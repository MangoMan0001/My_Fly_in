#!/usr/bin/env python3

from model import DroneNetwork, Zone

class ConsoleVisualizer:
    """ターミナルに整形して出力"""
    COLORS = {
        "green": "\033[92m",          # 明るい緑
        "blue": "\033[94m",           # 明るい青
        "red": "\033[91m",            # 明るい赤
        "yellow": "\033[93m",         # 明るい黄色
        "orange": "\033[38;5;214m",   # 鮮やかなオレンジ
        "cyan": "\033[96m",           # 明るい水色
        "purple": "\033[38;5;135m",   # 深みのある紫色
        "brown": "\033[38;5;130m",    # 落ち着いた茶色
        "lime": "\033[38;5;118m",     # 蛍光色のようなライムグリーン
        "magenta": "\033[95m",        # 鮮やかな赤紫（マゼンタ）
        "gold": "\033[38;5;220m",     # 輝くようなゴールド
        "black": "\033[30m",          # 黒（※背景が黒いターミナルでは見えなくなります）
        "maroon": "\033[38;5;52m",    # 暗い赤茶色（マルーン）
        "darkred": "\033[38;5;88m",   # 深い真紅
        "violet": "\033[38;5;177m",   # 柔らかい青紫色（スミレ色）
        "crimson": "\033[38;5;161m",  # 強い赤紫色（クリムゾン）
        "reset": "\033[0m"            # 【必須】色を元に戻すリセットコード
    }

    @classmethod
    def render_method(cls, network: DroneNetwork) -> None:
        """ターミナルに出力"""
        print("\n--- Turminal Output ---")
        for move_turn in network.history:
            color_line = []
            for move in move_turn:
                color_line.append(cls._color_move_string(move, network.zones))
            print(" ".join(color_line))
        print("-------------------------")
        cls._print_secondary_metrics(network)

    @classmethod
    def _color_move_string(cls, move_str: str, zones: dict[str, Zone]) -> str:
        """文字列を解析し、目標ゾーンのcolor属性に合わせて色を塗る"""
        target_zone = move_str.split('-')[-1]
        if target_zone not in zones:
            return move_str
        color_name = zones[target_zone].color
        if not color_name:
            return move_str
        if color_name.lower() == "rainbow":
            return cls._apply_rainbow(move_str)
        color_code = cls.COLORS.get(color_name.lower(), cls.COLORS['reset'])
        return f"{color_code}{move_str}{cls.COLORS['reset']}"

    @classmethod
    def _apply_rainbow(cls, text: str) -> str:
        """文字列を1文字ずつ虹色に輝かせる"""
        rainbow_palette = [
            cls.COLORS["red"], cls.COLORS["orange"], cls.COLORS["yellow"],
            cls.COLORS["green"], cls.COLORS["cyan"], cls.COLORS["blue"], cls.COLORS["purple"]
        ]
        result = ""
        for i, char in enumerate(text):
            result += rainbow_palette[i % len(rainbow_palette)] + char
        return result + cls.COLORS['reset']

    @classmethod
    def _print_secondary_metrics(cls, network: 'DroneNetwork') -> None:
        """シミュレーションの二次評価基準を計算して出力"""
        if not network.history or network.nb_drones == 0:
            return
        total_drones = len(network.drones)
        total_turns = len(network.history)
        total_moves = sum(len(turn) for turn in network.history)
        total_path_cost = 0
        for drone in network.drones:
            total_path_cost += drone.total_cost
        print(">>>    Performance    <<<")
        print(f" Total turn              : {total_turns} turn")
        print(f" Efficiency (Moves/Turn) : {total_moves / total_turns:.2f} drones/turn")
        print(f" Average Turns per Drone : {total_path_cost / total_drones:.2f} turns")
        print(f" Total Path Cost         : {total_path_cost} turns")
        print("=========================\n")

if __name__ == "__main__":
    pass
