#!/usr/bin/env python3

from enum import Enum
from typing import Optional
from collections import deque
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

# --- 1. 許可されたゾーンの種類を定義 ---
class ZoneType(str, Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

# --- 2. Zone (ノード) モデル ---
class Zone(BaseModel):
    name: str
    x: int
    y: int

    zone_type: ZoneType = Field(default=ZoneType.NORMAL)
    color: Optional[str] = Field(default=None)
    max_drones: int = Field(default=1, gt=0)
    parking_drones: list[str] = Field(default_factory=list)

    # 名前に「- (ダッシュ)」 か 「' '(スペース)」が含まれていないかチェック
    @field_validator('name')
    @classmethod
    def name_must_not_contain_dash_space(cls, v: str) -> str:
        if '-' in v:
            raise ValueError("Zone name cannot contain dashes")
        if ' ' in v:
            raise ValueError("Zone name cannot contain space")
        return v

    def can_accept_drone(self) -> bool:
        """ドローンが停められるかを返す"""
        if len(self.parking_drones) < self.max_drones:
            return True
        return False

    def add_drone(self, drone_name: str) -> None:
        """ゾーンにドローンを追加する"""
        self.parking_drones.append(drone_name)

    def remove_drone(self, drone_name: str) -> None:
        """ゾーンからドローンを削除する"""
        self.parking_drones.remove(drone_name)

# --- 3. Connection (エッジ) モデル ---
class Connection(BaseModel):
    zone1: str
    zone2: str
    max_link_capacity: int = Field(default=1, gt=0)

    # 自分自身との接続を弾く
    @model_validator(mode='after')
    def check_zones_are_different(self) -> 'Connection':
        if self.zone1 == self.zone2:
            raise ValueError(f"A zone cannot connect to itself: {self.zone1}")
        return self

# --- 4. Drone モデル ---
class Drone(BaseModel):
    """ドローン1機を管理するクラス"""
    id: str                          # "D1", "D2" などのID
    current_location: str            # 現在いるZoneまたはConnectionの名前
    is_delivered: bool = False       # ゴールに到達したかどうか
    path: list[str] | None = []      # ゴールまでの最短経路
    turn_end: bool = False           # 行動終了フラグ

    def act(self, network: DroneNetwork, is_deadlock: bool =False) -> bool:
        """ドローンが１ターン分行動する。動けないならスキップする"""
        # 最初とデッドロックしてる時に再検索
        if not self.path or is_deadlock:
            self.path = self._find_shortest_path(self.current_location,
                                                 network.end_zone_name,
                                                 network.adjacency_list)
            if self.path is None:
                raise ValueError(f"ドローン {self.id} がゴールへ到達できませんわ！ルートが孤立しておりますの！")
            self.path.pop(0)

        # 行けるなら行く
        if network.zones[self.path[0]].can_accept_drone():
            network.zones[self.current_location].remove_drone(self.id)
            network.zones[self.path[0]].add_drone(self.id)
            self.current_location = self.path[0]
            self.path.pop(0)
            if self.current_location == network.end_zone_name:
                self.is_delivered = True
            return True
        return False

    def _find_shortest_path(self,
                            start_zone: str,
                            target_zone: str,
                            adjacency_list: dict[str, list[str]]) -> Optional[list[str]]:
        """
        幅優先探索を用いて、start_zone から target_zone までの最短経路を探す
        """
        queue = deque([start_zone])

        came_from: dict[str, str | None]
        came_from = {start_zone: None}

        while queue:
            current = queue.popleft()
            if current == target_zone:
                break
            for next_name in adjacency_list[current]:
                if next_name not in came_from:
                    queue.append(next_name)
                    came_from[next_name] = current
        if target_zone not in came_from:
            return None

        path = []
        current_trace: str | None = target_zone
        while current_trace is not None:
            path.append(current_trace)
            current_trace = came_from[current_trace]

        path.reverse()
        return path

# --- 3. DroneNetwork (統括) モデル ---
class DroneNetwork(BaseModel):
    """
    ドローンネットワーク全体を管理する司令塔クラス。
    """
    # -- Model設定 (後から属性の中身が変わってもバリデーションが行われる) --
    model_config = ConfigDict(validate_assignment=True)
    # -- Mapの参照値 --
    nb_drones: int = Field(default=0, gt=0)                             # ドローン数
    start_zone_name: str = ""                                           # スタート位置のZone名
    end_zone_name: str = ""                                             # ゴール位置のZone名
    # -- 管理オブジェクト --
    drones: list[Drone] = Field(default_factory=list)                   # Droneオブジェクトをlistで保存
    zones: dict[str, Zone] = Field(default_factory=dict)                # Zone名とZoneオブジェクトを辞書で保存
    connections: list[Connection] = Field(default_factory=list)         # Connerctionオブジェクトをlistで保存
    # -- Other --
    history: list[list[str]] = Field(default_factory=list)              # 各ターンの出力文字列のリスト
    adjacency_list: dict[str, list[str]] = Field(default_factory=dict)  # 各ゾーンから接続されているゾーン名

    # --- Setter Method ---
    def add_zone(self, zone: Zone) -> None:
        if zone.name in self.zones:
            raise ValueError(f"Duplicate zonename detected: {zone.name}")
        for existing_zone in self.zones.values():
            if existing_zone.x == zone.x and existing_zone.y == zone.y:
                raise ValueError(f"Coordinate overlap detected: {zone.name} "
                                 f"and {existing_zone.name} are at ({zone.x}, {zone.y})")
        self.zones[zone.name] = zone

    def add_start_zone(self, zone: Zone) -> None:
        if self.start_zone_name:
            raise ValueError(f"two or more startzone settings detected: {zone.name}")
        self.add_zone(zone)
        self.start_zone_name = zone.name

    def add_end_zone(self, zone: Zone) -> None:
        if self.end_zone_name:
            raise ValueError(f"two or more endtzone settings detected: {zone.name}")
        self.add_zone(zone)
        self.end_zone_name = zone.name

    def add_connection(self, connection: Connection) -> None:
        if not connection.zone1 in self.zones or not connection.zone2 in self.zones:
            raise ValueError(f"Connection to an undefined zone detected: {connection.zone1}-{connection.zone2}")
        self.connections.append(connection)

    # --- Initialize and Validation Method ---
    def initialize(self) -> None:
        """初期化統括メソッド"""
        self._validate_network_integrity()
        self._build_adjacent_zones()
        self._initialize_drones()

    def _validate_network_integrity(self) -> None:
        """パース完了後に、ネットワーク全体に矛盾がないかチェック"""
        # 0. nb_dronesが設定されているかチェック
        if self.nb_drones is None:
            raise ValueError("nb_drones is missing or undefined.")

        # 1. startとendが設定されているかチェック
        if not self.start_zone_name or self.start_zone_name not in self.zones:
            raise ValueError("Start zone is missing or undefined.")
        if not self.end_zone_name or self.end_zone_name not in self.zones:
            raise ValueError("End zone is missing or undefined.")

        seen_connections = set()
        for conn in self.connections:
            # 2. Connectionが実在するゾーンを結んでいるかチェック
            if conn.zone1 not in self.zones or conn.zone2 not in self.zones:
                raise ValueError(f"Connection links to undefined zones: {conn.zone1}-{conn.zone2}")

            # 3. 重複チェック
            edge = tuple(sorted([conn.zone1, conn.zone2]))
            if edge in seen_connections:
                raise ValueError(f"Duplicate connection detected: {conn.zone1}-{conn.zone2}")
            seen_connections.add(edge)

    def _build_adjacent_zones(self) -> None:
        """各ゾーンに隣接したゾーンをリストで紐づけた辞書を作成する"""
        for name in self.zones:
            self.adjacency_list[name] = []
        for conn in self.connections:
            self.adjacency_list[conn.zone1].append(conn.zone2)
            self.adjacency_list[conn.zone2].append(conn.zone1)

    def _initialize_drones(self) -> None:
        """スタート地点に全ドローンを配置"""
        for i in range(1, self.nb_drones + 1):
            self.drones.append(Drone(id=f"D{i}",
                               current_location=self.start_zone_name))
            self.zones[self.start_zone_name].add_drone(self.drones[-1].id)
        self.zones[self.end_zone_name].max_drones = self.nb_drones
        # debug mesage
        print(f"{self.nb_drones}機のドローンが {self.start_zone_name} に配置されましたわ！")

    # --- シミュレーションメソッド ---
    def simulate(self) -> None:
        """シミュレーションを実行"""
        while any(not drone.is_delivered for drone in self.drones):
            runner_drones = [drone for drone in self.drones if not drone.is_delivered]
            self._simulate_turn(runner_drones)
            runner_drones = []

    def _simulate_turn(self, unmove_drones: list[Drone]) -> None:
        """１ターンごとにシミュレーションを進める"""
        is_deadlock: bool = False
        turn_moves = []
        while unmove_drones:
            is_move: bool = False
            next_unmove_drones: list[Drone] = []
            for drone in unmove_drones:
                if drone.act(self, is_deadlock):
                    is_move = True
                    turn_moves.append(f"{drone.id}-{drone.current_location}")
                else:
                    next_unmove_drones.append(drone)
            unmove_drones = next_unmove_drones
            if not is_move:
                if is_deadlock:
                    break
                is_deadlock = True
            else:
                is_deadlock = False

        # 1ターン分の動きを記録
        self._record_turn(turn_moves)

    def _record_turn(self, turn_moves: list[str]) -> None:
        """1ターン分の移動記録を履歴に保存"""
        if turn_moves:
            self.history.append(turn_moves)

    def print_history(self) -> None:
        """記録した履歴を出力"""
        print("\n--- Simulation Output ---")
        for turn in self.history:
            print(" ".join(turn))
        print("-------------------------\n")

    # --- utiles method ---
    def get_adjacent_zones(self, zone_name: str) -> list[Zone]:
        """指定したゾーンに隣接しているゾーンのリストを返します"""
        return [self.zones[name] for name in self.adjacency_list[zone_name]]

    def simulate_step(self) -> None:
        """
        1ターンのシミュレーションを進めます
        全ドローンの移動計画を立て、競合がないか確認し、移動を実行
        """
        pass

if __name__ == "__main__":
    pass
