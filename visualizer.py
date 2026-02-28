#!/usr/bin/env python3

from model import DroneNetwork, Zone, ZoneType
import pygame
import sys

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

    "cap_bg": (20, 20, 20),        # 限りなく黒に近いステルスブラック
    "cap_text": (255, 176, 0),     # 鮮烈なハザード・アンバー（琥珀色）
    "cap_border": (90, 90, 100),   # 無骨なガンメタルグレー

    "line": (100, 100, 120)       # コネクションの線の色
}

RAINBOW_PALETTE = [RGB_COLORS["red"],
                   RGB_COLORS["orange"],
                   RGB_COLORS["yellow"],
                   RGB_COLORS["green"],
                   RGB_COLORS["cyan"],
                   RGB_COLORS["blue"],
                   RGB_COLORS["purple"]]

class ConsoleVisualizer:
    """ターミナルに整形して出力"""

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

        color_code = COLORS.get(color_name.lower(), COLORS['reset'])
        return f"{color_code}{move_str}{COLORS['reset']}"

    @classmethod
    def _apply_rainbow(cls, text: str) -> str:
        """文字列を1文字ずつ虹色に輝かせる"""
        rainbow_palette = [
            COLORS["red"], COLORS["orange"], COLORS["yellow"],
            COLORS["green"], COLORS["cyan"], COLORS["blue"], COLORS["purple"]
        ]
        result = ""
        for i, char in enumerate(text):
            result += rainbow_palette[i % len(rainbow_palette)] + char
        return result + COLORS['reset']

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
    """GUIとしてMapの可視化を担うクラス"""

    def __init__(self, width: int, height: int):
        """初期化"""
        self.file_name: str = ""
        self.screen_width: int = width
        self.screen_height: int = height
        self.current_turn: int = 0
        self.max_turn: int = 0
        self.scale: float = 0
        self.offset_x: float = 0
        self.offset_y: float = 0
        self.r: int = 0
        self.snapshots: list[dict[str,list[str]]] = []
        self.screen: pygame.Surface
        self.show_capacity: bool = False

    def rend_gui(self, network: DroneNetwork, file_name: str) -> None:
        """GUIとしてマップをレンダリングする"""
        self.file_name = file_name
        self._calculate_scale(network)
        self._run_pygame(network)

    def _calculate_scale(self, network: DroneNetwork) -> None:
        """座標調整の倍率計算"""
        # 1. マップの最小・最大のX, Yを調べる
        min_x = min(z.x for z in network.zones.values())
        max_x = max(z.x for z in network.zones.values())
        min_y = min(z.y for z in network.zones.values())
        max_y = max(z.y for z in network.zones.values())

        map_width = max_x - min_x
        map_height = max_y - min_y

        # 2. 画面の描画に使えるサイズ (1080, 520)
        drawable_width = self.screen_width - 200
        drawable_height = self.screen_height - 200

        # 3. 倍率（スケール）の計算(スケールとは1マス何ピクセルにするかということ)
        scale_x = drawable_width / map_width if map_width > 0 else float('inf')
        scale_y = drawable_height / map_height if map_height > 0 else float('inf')

        scale = min(scale_x, scale_y)
        if scale == float('inf'):
            scale = 100.0

        # 4. ズレ（オフセット）の計算
        screen_cx = self.screen_width / 2
        screen_cy = self.screen_height / 2

        map_cx = (min_x + max_x) / 2
        map_cy = (min_y + max_y) / 2

        self.offset_x = screen_cx - (map_cx * scale)
        self.offset_y = screen_cy - (map_cy * scale)
        if scale < 3.0:
            raise ValueError("\nThe MAP size is too large to generate the GUI.")
        self.r = max(10, min(int(scale * 0.25), 30))
        self.scale = scale

    def _run_pygame(self, network:DroneNetwork) -> None:
        """pygameを動かす"""
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption(f"Drone Network Visualizer - {self.file_name}")
        clock = pygame.time.Clock()
        self._generate_snapshots(network)

        running = True
        # --- 描画開始 ---
        while running:
            self._handle_event()
            self._draw_maps(network)
            self._draw_ui()

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

    def _generate_snapshots(self, network: 'DroneNetwork') -> None:
        """ターン数ごとに、ゾーンとそこに存在したドローンを並べたリストを作成する"""
        current_positions = {drone.id: network.start_zone_name for drone in network.drones}

        # 1. 全ドローンをスタート地点に設置
        turn0_state: dict[str, list[str]] = {}
        for d_id, pos in current_positions.items():
            if pos not in turn0_state:
                turn0_state[pos] = []
            turn0_state[pos].append(d_id)
        self.snapshots.append(turn0_state)

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
            self.snapshots.append(new_state)
            self.max_turn = len(self.snapshots) - 1

    def _handle_event(self) -> None:
        """バツで閉じるやターン再生などのイベント処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT \
                    and self.current_turn < self.max_turn:
                    self.current_turn += 1
                elif event.key == pygame.K_LEFT \
                    and 0 < self.current_turn:
                    self.current_turn -= 1
                elif event.key == pygame.K_RETURN:
                    self.current_turn = 0
                elif event.key == pygame.K_TAB:
                    self.show_capacity = not self.show_capacity

    def _draw_maps(self,network: 'DroneNetwork') -> None:
        """移動経路、ゾーン、ドローンを描画する"""
        self.screen.fill(RGB_COLORS['bg'])
        self._draw_line(network)
        self._draw_zone(network)
        self._draw_drone(network)

    def _draw_line(self,network: DroneNetwork) -> None:
        """ゾーン間の移動経路を描画"""
        for conn in network.connections:
            z1 = network.zones[conn.zone1]
            z2 = network.zones[conn.zone2]
            # 描画座標は(zone座標 * 倍率 + zone中心と画面中心とのズレ)で求められる
            pos1 = (int(z1.x * self.scale + self.offset_x),
                    int(z1.y * self.scale + self.offset_y))
            pos2 = (int(z2.x * self.scale + self.offset_x),
                    int(z2.y * self.scale + self.offset_y))
            pygame.draw.line(self.screen, RGB_COLORS['line'], pos1, pos2, 3)

    def _draw_zone(self,network: 'DroneNetwork') -> None:
        """ゾーンの描画を行う"""
        for zone in network.zones.values():
            r = self.r
            pos = (int(zone.x * self.scale + self.offset_x),
                   int(zone.y * self.scale + self.offset_y))
            # 色付け描画
            color_name = zone.color if zone.color else 'default'
            if color_name.lower() == "rainbow":
                time_ms = pygame.time.get_ticks()
                color_idx = (time_ms // 200) % len(RAINBOW_PALETTE)
                color_code = RAINBOW_PALETTE[color_idx]
            else:
                color_code = RGB_COLORS.get(color_name, RGB_COLORS['default'])
            # 形の描き分け
            if zone.zone_type == ZoneType.NORMAL:
                pygame.draw.circle(self.screen, color_code, pos, r)
            elif zone.zone_type == ZoneType.RESTRICTED:
                rect_area = (pos[0] - r, pos[1] - r, r * 2, r * 2)
                pygame.draw.rect(self.screen, color_code, rect_area)
            elif zone.zone_type == ZoneType.PRIORITY:
                points = [(pos[0], pos[1] - r), # 上
                          (pos[0] + r, pos[1]), # 右
                          (pos[0], pos[1] + r), # 下
                          (pos[0] - r, pos[1])] # 左
                pygame.draw.polygon(self.screen, color_code, points)
            elif zone.zone_type == ZoneType.BLOCKED:
                pygame.draw.line(self.screen, color_code,
                                 (pos[0] - r, pos[1] - r),
                                 (pos[0] + r, pos[1] + r), 6)
                pygame.draw.line(self.screen, color_code,
                                 (pos[0] + r, pos[1] - r),
                                 (pos[0] - r, pos[1] + r), 6)

            cap_font = pygame.font.SysFont(None, 24)
            if self.show_capacity:
                cap_text_str = str(zone.max_drones)

                pygame.draw.circle(self.screen, RGB_COLORS['cap_bg'], pos, 14)
                pygame.draw.circle(self.screen, RGB_COLORS['cap_border'], pos, 14, 2) # 太さ2px

                font = pygame.font.SysFont(None, 22) # ドローンより少し大きめ
                cap_surface = font.render(cap_text_str, True, RGB_COLORS['cap_text'])
                text_rect = cap_surface.get_rect(center=pos)
                self.screen.blit(cap_surface, text_rect)

    def _draw_drone(self,network: 'DroneNetwork') -> None:
        """ドローンを描画"""
        if self.show_capacity:
            return
        current_snap = self.snapshots[self.current_turn]
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
            pos = (int(map_x * self.scale + self.offset_x),
                   int(map_y * self.scale + self.offset_y))
            pygame.draw.circle(self.screen, RGB_COLORS['drone'], pos, 9)

            font = pygame.font.SysFont(None, 20)
            count_text = font.render(str(drone_count), True, RGB_COLORS['black'])
            text_rect = count_text.get_rect(center=pos)
            self.screen.blit(count_text, text_rect)

    def _draw_ui(self) -> None:
        """uiを描画"""
        turn_font = pygame.font.SysFont(None, 36)
        turn_text = turn_font.render(f"Turn: {self.current_turn} / {self.max_turn}",
                                     True, RGB_COLORS['turn'])
        self.screen.blit(turn_text, (20, 20))
        if self.show_capacity:
            turn_text = turn_font.render(f"Capacity",
                                         True, RGB_COLORS['cap_text'])
            self.screen.blit(turn_text, (200, 20))
        font_text = turn_font.render("NORMAL - Circle    "
                                     "RESTRICTED - Square    "
                                     "PRIORITY - Diamond    "
                                     "BLOCKED - Cross",
                                     True, RGB_COLORS['turn'])
        self.screen.blit(font_text, (20, self.screen_height - 40))

if __name__ == "__main__":
    pass
