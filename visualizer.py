#!/usr/bin/env python3
"""Module for visualizing the drone network."""

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
    "black": "\033[30m",          # 黒
    "maroon": "\033[38;5;52m",    # 暗い赤茶色（マルーン）
    "darkred": "\033[38;5;88m",   # 深い真紅
    "violet": "\033[38;5;177m",   # 柔らかい青紫色（スミレ色）
    "crimson": "\033[38;5;161m",  # 強い赤紫色（クリムゾン）
    "reset": "\033[0m"            # 色を元に戻すリセットコード
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
    "crimson": (220, 20, 60),     # クリムゾン

    "default": (200, 200, 200),   # 指定がない時の白灰色
    "bg": (30, 30, 40),           # 背景のダークグレー
    "line": (100, 100, 120),      # コネクションの線の色
    "drone": (255, 255, 255),     # ドローン
    "turn": (255, 255, 255),      # ターン表記

    "cap_bg": (20, 20, 20),       # 限りなく黒に近いステルスブラック
    "cap_text": (255, 176, 0),    # 鮮烈なハザード・アンバー（琥珀色）
    "cap_border": (90, 90, 100)   # 無骨なガンメタルグレー
}

RAINBOW_PALETTE = [
    RGB_COLORS["red"],
    RGB_COLORS["orange"],
    RGB_COLORS["yellow"],
    RGB_COLORS["green"],
    RGB_COLORS["cyan"],
    RGB_COLORS["blue"],
    RGB_COLORS["purple"]
]


class ConsoleVisualizer:
    """Visualizer for printing formatted output to the terminal."""

    @classmethod
    def render_method(cls, network: DroneNetwork) -> None:
        """Print the simulation history to the terminal.

        Args:
            network (DroneNetwork): The drone network to visualize.
        """
        print("\n--- Terminal Output ---")
        for move_turn in network.history:
            color_line = []
            for move in move_turn:
                color_line.append(cls._color_move_string(move, network.zones))
            print(" ".join(color_line))
        print("-------------------------")
        cls._print_secondary_metrics(network)

    @classmethod
    def _color_move_string(cls, move_str: str, zones: dict[str, Zone]) -> str:
        """Parse a movement string and apply the target zone's color.

        Args:
            move_str (str): The movement string (e.g., 'D1-roof1').
            zones (dict[str, Zone]): A dictionary mapping zone names to Zone.

        Returns:
            str: The colored movement string for terminal output.
        """
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
        """Apply a rainbow color effect to the given text.

        Args:
            text (str): The text to be colored.

        Returns:
            str: The text formatted with rainbow terminal colors.
        """
        rainbow_palette = [
            COLORS["red"], COLORS["orange"], COLORS["yellow"],
            COLORS["green"], COLORS["cyan"], COLORS["blue"], COLORS["purple"]
        ]
        result = ""
        for i, char in enumerate(text):
            result += rainbow_palette[i % len(rainbow_palette)] + char
        return result + COLORS['reset']

    @classmethod
    def _print_secondary_metrics(cls, network: DroneNetwork) -> None:
        """Calculate and print secondary metrics of the simulation.

        Args:
            network (DroneNetwork): The network containing simulation data.
        """
        if not network.history or network.nb_drones == 0:
            return
        total_drones = len(network.drones)
        total_turns = len(network.history)
        total_moves = sum(len(turn) for turn in network.history)
        total_path_cost = 0
        for drone in network.drones:
            total_path_cost += drone.total_cost
        print(">>>    Performance    <<<")
        print(f" Total turn              : {total_turns} turns")
        print(" Efficiency (Moves/Turn) : "
              f"{total_moves / total_turns:.2f} drones/turn")
        print(" Average Turns per Drone : "
              f"{total_path_cost / total_drones:.2f} turns")
        print(f" Total Path Cost         : {total_path_cost} turns")
        print("=========================\n")


class GraphicVisualizer:
    """GUI visualizer for rendering the map and drone movements."""

    def __init__(self, width: int, height: int):
        """Initialize the graphic visualizer with screen dimensions.

        Args:
            width (int): The width of the pygame window.
            height (int): The height of the pygame window.
        """
        self.file_name: str = ""
        self.screen_width: int = width
        self.screen_height: int = height
        self.current_turn: int = 0
        self.max_turn: int = 0
        self.scale: float = 0
        self.offset_x: float = 0
        self.offset_y: float = 0
        self.r: int = 0
        self.snapshots: list[dict[str, list[str]]] = []
        self.screen: pygame.Surface
        self.show_capacity: bool = False

    def rend_gui(self, network: DroneNetwork, file_name: str) -> None:
        """Render the map and start the GUI visualization.

        Args:
            network (DroneNetwork): The drone network to visualize.
            file_name (str): name of the input_file to display in the title.
        """
        self.file_name = file_name
        self._calculate_scale(network)
        self._run_pygame(network)

    def _calculate_scale(self, network: DroneNetwork) -> None:
        """Calculate the scale and offset for drawing the map on screen.

        Args:
            network (DroneNetwork): The network containing zone coordinates.

        Raises:
            ValueError: If the calculated scale is too small to render.
        """
        min_x = min(z.x for z in network.zones.values())
        max_x = max(z.x for z in network.zones.values())
        min_y = min(z.y for z in network.zones.values())
        max_y = max(z.y for z in network.zones.values())

        map_width = max_x - min_x
        map_height = max_y - min_y

        drawable_width = self.screen_width - 200
        drawable_height = self.screen_height - 200

        # 3. 倍率（スケール）の計算(スケールとは1マス何ピクセルにするかということ)
        scale_x = drawable_width / map_width if map_width > 0 else float('inf')
        scale_y = (
            drawable_height / map_height if map_height > 0 else float('inf')
            )

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
            raise ValueError(
                "\nThe MAP size is too large to generate the GUI."
                )

        self.r = max(10, min(int(scale * 0.25), 30))
        self.scale = scale

    def _run_pygame(self, network: DroneNetwork) -> None:
        """Initialize pygame and run the main rendering loop.

        Args:
            network (DroneNetwork): The drone network to visualize.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width,
                                               self.screen_height))
        pygame.display.set_caption(
            f"Drone Network Visualizer - {self.file_name}"
            )
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

    def _generate_snapshots(self, network: DroneNetwork) -> None:
        """Create a list of drone positions for each turn.

        Args:
            network (DroneNetwork): network containing the movement history.
        """
        current_positions = {
            drone.id: network.start_zone_name for drone in network.drones
            }

        # 1. 全ドローンをスタート地点に設置
        turn0_state: dict[str, list[str]] = {}
        for d_id, pos in current_positions.items():
            if pos not in turn0_state:
                turn0_state[pos] = []
            turn0_state[pos].append(d_id)
        self.snapshots.append(turn0_state)

        # 2. historyを読み込みながら各ターンでのドローンの所属地点を記録する
        for turn_moves in network.history:
            for move in turn_moves:
                parts = move.split('-', 1)
                drone_id = parts[0]
                target_place = parts[1]
                current_positions[drone_id] = target_place

            # 3. このターンで各ゾーンに所属するドローンIDを記録する
            new_state: dict[str, list[str]] = {}
            for d_id, pos in current_positions.items():
                if pos not in new_state:
                    new_state[pos] = []
                new_state[pos].append(d_id)
            # 4. snapshotsは各ターン毎に各ゾーンに所属するドローンIDのリストを記録する
            self.snapshots.append(new_state)

        self.max_turn = len(self.snapshots) - 1

    def _handle_event(self) -> None:
        """Handle user input events like key presses and window closing."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_RIGHT
                   and self.current_turn < self.max_turn):
                    self.current_turn += 1
                elif (event.key == pygame.K_LEFT
                      and 0 < self.current_turn):
                    self.current_turn -= 1
                elif event.key == pygame.K_RETURN:
                    self.current_turn = 0
                elif event.key == pygame.K_TAB:
                    self.show_capacity = not self.show_capacity

    def _draw_maps(self, network: DroneNetwork) -> None:
        """Draw the background, lines, zones, and drones.

        Args:
            network (DroneNetwork): The network to render.
        """
        self.screen.fill(RGB_COLORS['bg'])
        self._draw_line(network)
        self._draw_zone(network)
        self._draw_drone(network)

    def _draw_line(self, network: DroneNetwork) -> None:
        """Draw connection lines between zones.

        Args:
            network (DroneNetwork): The network containing connections.
        """
        for conn in network.connections:
            z1 = network.zones[conn.zone1]
            z2 = network.zones[conn.zone2]
            # 描画座標は(zone座標 * 倍率 + zone中心と画面中心とのズレ)で求められる
            pos1 = (int(z1.x * self.scale + self.offset_x),
                    int(z1.y * self.scale + self.offset_y))
            pos2 = (int(z2.x * self.scale + self.offset_x),
                    int(z2.y * self.scale + self.offset_y))
            pygame.draw.line(self.screen, RGB_COLORS['line'], pos1, pos2, 3)

    def _draw_zone(self, network: DroneNetwork) -> None:
        """Draw all zones with their specific shapes and colors.

        Args:
            network (DroneNetwork): The network containing zones.
        """
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
                points = [(pos[0], pos[1] - r),
                          (pos[0] + r, pos[1]),
                          (pos[0], pos[1] + r),
                          (pos[0] - r, pos[1])]
                pygame.draw.polygon(self.screen, color_code, points)
            elif zone.zone_type == ZoneType.BLOCKED:
                pygame.draw.line(self.screen, color_code,
                                 (pos[0] - r, pos[1] - r),
                                 (pos[0] + r, pos[1] + r), 6)
                pygame.draw.line(self.screen, color_code,
                                 (pos[0] + r, pos[1] - r),
                                 (pos[0] - r, pos[1] + r), 6)

            if self.show_capacity:
                cap_text_str = str(zone.max_drones)
                pygame.draw.circle(self.screen, RGB_COLORS['cap_bg'], pos, 14)
                pygame.draw.circle(self.screen, RGB_COLORS['cap_border'],
                                   pos, 14, 2)
                font = pygame.font.SysFont(None, 22)
                cap_surface = font.render(cap_text_str, True,
                                          RGB_COLORS['cap_text'])
                text_rect = cap_surface.get_rect(center=pos)
                self.screen.blit(cap_surface, text_rect)

    def _draw_drone(self, network: DroneNetwork) -> None:
        """Draw drones at their current positions for the active turn.

        Args:
            network (DroneNetwork): The network containing zone data.
        """
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
            count_text = font.render(str(drone_count), True,
                                     RGB_COLORS['black'])
            text_rect = count_text.get_rect(center=pos)
            self.screen.blit(count_text, text_rect)

    def _draw_ui(self) -> None:
        """Draw the user interface text and legends."""
        turn_font = pygame.font.SysFont(None, 36)
        turn_text = turn_font.render(
            f"Turn: {self.current_turn} / {self.max_turn}",
            True, RGB_COLORS['turn']
            )
        self.screen.blit(turn_text, (20, 20))

        if self.show_capacity:
            turn_text = turn_font.render("Capacity",
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
