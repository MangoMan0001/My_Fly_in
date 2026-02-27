#!/usr/bin/env python3

from model import DroneNetwork, Zone, ZoneType
import pygame
import sys


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

class GraphicVisualizer:
    RGB_COLORS = {
        "green": (50, 205, 50),       # 鮮やかな緑（ライムグリーン）
        "blue": (65, 105, 225),       # ロイヤルブルー
        "red": (220, 20, 60),         # クリムゾンレッド
        "yellow": (255, 215, 0),      # ゴールド寄りの黄色
        "orange": (255, 140, 0),      # ダークオレンジ
        "cyan": (0, 255, 255),        # シアン（水色）
        "purple": (147, 112, 219),    # ミディアムパープル
        "brown": (139, 69, 19),       # サドルブラウン（落ち着いた茶色）
        "lime": (0, 255, 0),          # ピュアなライム（純緑）
        "magenta": (255, 0, 255),     # マゼンタ（赤紫）
        "gold": (218, 165, 32),       # ゴールデンロッド（渋い金）
        "black": (0, 0, 0),           # 真っ黒
        "maroon": (128, 0, 0),        # マルーン（暗い赤茶色）
        "darkred": (139, 0, 0),       # ダークレッド
        "violet": (238, 130, 238),    # バイオレット（スミレ色）
        "crimson": (220, 20, 60),     # クリムゾン（強い赤紫 ※redと同じにして統一感を出してますわ）

        "default": (200, 200, 200),   # 指定がない時の白灰色
        "bg": (30, 30, 40),           # 背景のダークグレー
        "drone": (255, 255, 255),     # ドローン
        "turn": (255, 255, 255),      # ターン表記
        "line": (100, 100, 120)       # コネクションの線の色
    }

    @classmethod
    def rend_gui(cls, network: DroneNetwork, file_name: str) -> None:
        """GUIとしてマップをレンダリングする"""
        # 0. 必要な変数を初期化
        screen_width, screen_height = 1280, 720
        current_turn = 0

        # 1. 座標を中心に調整するための倍率を計算
        scale, offset_x, offset_y = cls._calculate_scale(network, screen_width, screen_height)
        if scale < 3.0:
            print("\n⚠️ 【警告】マップが広大すぎるため、GUIビジュアライザの描画をスキップしますわ！")
            pygame.quit()
            return # ここで処理を終わらせます
        r = max(10, min(int(scale * 0.15), 30))

        # 2. ヴィジュアライザーの初期化
        pygame.init()
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption(f"Drone Network Visualizer - {file_name}")
        clock = pygame.time.Clock()
        snapshots = cls._generate_snapshots(network)
        max_turn = len(snapshots) - 1

        running = True
        # 3. pygameによる描画開始
        while running:
            # --- A. イベント処理（×ボタンで閉じる） ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT and current_turn < max_turn:
                        current_turn += 1
                    elif event.key == pygame.K_LEFT and 0 < current_turn:
                        current_turn -= 1
                    elif event.key == pygame.K_RETURN:
                        current_turn = 0

            # --- B. 画面の初期化 ---
            screen.fill(cls.RGB_COLORS['bg'])

            # --- C. 描画処理 ---
            #　線を描画
            for conn in network.connections:
                z1 = network.zones[conn.zone1]
                z2 = network.zones[conn.zone2]
                # 描画座標は(zone座標 * 倍率 + zone中心と画面中心とのズレ)で求められる
                pos1 = (int(z1.x * scale + offset_x), int(z1.y * scale + offset_y))
                pos2 = (int(z2.x * scale + offset_x), int(z2.y * scale + offset_y))
                # 線の描画
                pygame.draw.line(screen, cls.RGB_COLORS['line'], pos1, pos2, 3)

            # ゾーンを描画
            for zone in network.zones.values():
                pos = (int(zone.x * scale + offset_x), int(zone.y * scale + offset_y))
                # 色付け
                color_name = zone.color if zone.color else 'default'
                color_code = cls.RGB_COLORS.get(color_name, cls.RGB_COLORS['default'])
                if zone.zone_type == ZoneType.NORMAL:
                    pygame.draw.circle(screen, color_code, pos, r)
                elif zone.zone_type == ZoneType.RESTRICTED:

                    pygame.draw.circle(screen, color_code, pos, r)

            # ドローンを描画
            current_snap = snapshots[current_turn]
            for location, ids in current_snap.items():
                drone_count = len(ids)
                if '-' in location:
                    z1_name, z2_name = location.split('-')
                    z1, z2 = network.zones[z1_name], network.zones[z2_name]
                    map_x = (z1.x + z2.x) / 2
                    map_y = (z1.y + z2.y) / 2
                else:
                    map_x = network.zones[location].x
                    map_y = network.zones[location].y
                pos = (int(map_x * scale + offset_x), int(map_y * scale + offset_y))
                pygame.draw.circle(screen, cls.RGB_COLORS['drone'], pos, 9)
                font = pygame.font.SysFont(None, 20)
                count_text = font.render(str(drone_count), True, cls.RGB_COLORS['black'])
                text_rect = count_text.get_rect(center=pos)
                screen.blit(count_text, text_rect)
            turn_font = pygame.font.SysFont(None, 36)
            turn_text = turn_font.render(f"Turn: {current_turn} / {max_turn}", True, cls.RGB_COLORS['turn'])
            screen.blit(turn_text, (20, 20))

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

    @classmethod
    def _calculate_scale(cls, network: 'DroneNetwork',
                         screen_width: int, screen_height: int) -> tuple[float, float, float]:
        """マップを画面中央に収めるための (倍率, Xズレ, Yズレ) を計算して返す"""
        # 1. マップの最小・最大のX, Yを調べる
        min_x = min(z.x for z in network.zones.values())
        max_x = max(z.x for z in network.zones.values())
        min_y = min(z.y for z in network.zones.values())
        max_y = max(z.y for z in network.zones.values())

        map_width = max_x - min_x
        map_height = max_y - min_y

        # 2. 画面の描画に使えるサイズ (1080, 520)
        drawable_width = screen_width - 200
        drawable_height = screen_height - 200

        # 3. 倍率（スケール）の計算(スケールとは1マス何ピクセルにするかということ)
        scale_x = drawable_width / map_width if map_width > 0 else float('inf')
        scale_y = drawable_height / map_height if map_height > 0 else float('inf')

        scale = min(scale_x, scale_y)
        if scale == float('inf'):
            scale = 100.0

        # 4. ズレ（オフセット）の計算
        screen_cx = screen_width / 2
        screen_cy = screen_height / 2

        map_cx = (min_x + max_x) / 2
        map_cy = (min_y + max_y) / 2

        offset_x = screen_cx - (map_cx * scale)
        offset_y = screen_cy - (map_cy * scale)

        return scale, offset_x, offset_y

    @classmethod
    def _generate_snapshots(cls, network: 'DroneNetwork') -> list[dict[str, list[str]]]:
        """ターン数ごとに、ゾーンとそこに存在したドローンを並べたリストを作成する"""

        snapshots = []

        current_positions = {drone.id: network.start_zone_name for drone in network.drones}

        # 1. 全ドローンをスタート地点に設置
        turn0_state: dict[str, list[str]] = {}
        for d_id, pos in current_positions.items():
            if pos not in turn0_state:
                turn0_state[pos] = []
            turn0_state[pos].append(d_id)
        snapshots.append(turn0_state)

        # 2. 履歴（history）を1ターンずつ読み込んで、時間を進めますわ！
        for turn_moves in network.history:
            for move in turn_moves:
                parts = move.split('-', 1)
                drone_id = parts[0]
                target_place = parts[1]
                current_positions[drone_id] = target_place

            # 3. このターンが終了した時点での写真を撮りますの！
            new_state: dict[str, list[str]] = {}
            for d_id, pos in current_positions.items():
                if pos not in new_state:
                    new_state[pos] = []
                new_state[pos].append(d_id)

            snapshots.append(new_state)

        return snapshots

if __name__ == "__main__":
    pass
