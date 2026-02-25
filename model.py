#!/usr/bin/env python3

from enum import Enum
from typing import Optional, Any
from collections import deque
import heapq
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
    parking_drones: dict[int, int] = Field(default_factory=dict)        # 時空間滞在データ[ターン数: drone数]
    connections: dict[str, Connection] = Field(default_factory=dict)    # 接続されたコネクション[ゾーン: コネクション]
    neignbors: list[Zone] = Field(default_factory=list)                 # 隣人

    # 名前に「- (ダッシュ)」 か 「' '(スペース)」が含まれていないかチェック
    @field_validator('name')
    @classmethod
    def name_must_not_contain_dash_space(cls, v: str) -> str:
        if '-' in v:
            raise ValueError("Zone name cannot contain dashes")
        if ' ' in v:
            raise ValueError("Zone name cannot contain space")
        return v

    def can_accept_drone(self, turn: int, zone: Zone) -> bool:
        """指定されたターンにドローンが停められるかを返す"""
        if self.zone_type == ZoneType.BLOCKED:
            return False
        conn = self.connections[zone.name]
        if self.parking_drones.get(turn, 0) < self.max_drones:
            return conn.can_connect_drone(turn)
        return False

    def can_wait_drone(self, turn: int) -> bool:
        """1ターンドローンを待機できるか返す"""
        if self.zone_type == ZoneType.BLOCKED:
            return False
        if self.parking_drones.get(turn, 0) < self.max_drones:
            return True
        return False

    def add_drone(self, turn: int, zone: Zone) -> None:
        """指定されたターンにドローンを追加する"""
        conn = self.connections[zone.name]
        if self.can_accept_drone(turn, zone):
            conn.connect_drone(turn)
            self.parking_drones[turn] += 1
        raise ValueError("The zoen are already at maximum capacity")

    def get_cost(self) -> int:
        """このゾーンへ接続するためのコストを返す"""
        if self.zone_type == ZoneType.RESTRICTED:
            return 2
        return 1

# --- 3. Connection (エッジ) モデル ---
class Connection(BaseModel):
    name: str
    zone1: str
    zone2: str
    max_link_capacity: int = Field(default=1, gt=0)
    parking_drones: dict[int, int] = Field(default_factory=dict)        # 時空間滞在データ[ターン数: drone数]

    # 自分自身との接続を弾く
    @model_validator(mode='after')
    def check_zones_are_different(self) -> 'Connection':
        if self.zone1 == self.zone2:
            raise ValueError(f"A zone cannot connect to itself: {self.zone1}")
        return self

    def can_connect_drone(self, turn: int) -> bool:
        """指定されたターンにドローンが接続できるかを返す"""
        if self.parking_drones.get(turn, 0) < self.max_link_capacity:
            return True
        return False

    def connect_drone(self, turn: int) -> None:
        """指定されたターンにドローンを接続する"""
        if self.can_connect_drone(turn):
            self.parking_drones[turn] += 1
        raise ValueError("The connections are already at maximum capacity")

# --- 4. Drone モデル ---
class Drone(BaseModel):
    """ドローン1機を管理するクラス"""
    id: str                          # "D1", "D2" などのID
    current_location: str            # 現在いるZoneまたはConnectionの名前
    is_delivered: bool = False       # ゴールに到達したかどうか
    path: deque[str] = deque()             # ゴールまでの最短経路
    turn_end: bool = False           # 行動終了フラグ

    def act(self) -> str:
        """ドローンが１ターン分行動する。動けないならスキップする"""
        move = self.path.popleft()
        if move == "Wa-it":
            return ""
        return f"{self.id}-{move}"

    def find_shortest_path(self,
                           start_zone: Zone,
                           target_zone: Zone) -> None:
        """時空間ダイクストラ法を用いた最短経路探索"""
        # キューに入れるデータ: (総ターン数, -優先ゾーン通過数, 現在のゾーン, 経路のリスト)
        queue: list[Any] = []
        heapq.heappush(queue, (0, 0, start_zone.name, start_zone, [start_zone.name]))

        # 訪問済みの管理
        # set(ゾーン名, そのゾーンに着いた時の最小ターン数)
        visited: set[tuple[str, int]] = set()
        while queue:
            cost, priority, _, current, path = heapq.heappop(queue)

            # 時間軸が同じだったことがないか確認
            state = (current.name, cost)
            if state in visited:
                continue
            visited.add(state)

            # ゴールなら終了
            if current.name == target_zone.name:
                self.path = deque(path)
                # ここで実際の予約を行いたい
                return

            # 待機できるならキューに追加
            if current.can_wait_drone(cost + 1):
                heapq.heappush(queue, (cost + 1, priority, current.name,
                                       current, path + ["Wa-it"]))

            # 隣接ゾーンへ移動
            for neignbor in current.neignbors:
                if neignbor.zone_type == ZoneType.PRIORITY:
                    priority -= 1

                if neignbor.zone_type == ZoneType.RESTRICTED:
                    if not neignbor.connections[current.name].can_connect_drone(cost + 1):
                        continue
                    if neignbor.can_accept_drone(cost + 2, current):
                        turn_path = [neignbor.connections[current.name].name] + [neignbor.name]
                        heapq.heappush(queue,
                                       (cost + 2, priority, neignbor.name, neignbor,
                                        path + turn_path))
                    continue

                if neignbor.can_accept_drone(cost + 1, current):
                    heapq.heappush(queue, (cost + 1, priority, neignbor.name,
                                       neignbor, path + [neignbor.name]))

# --- 3. DroneNetwork (統括) モデル ---
class DroneNetwork(BaseModel):
    """
    ドローンネットワーク全体を管理する司令塔クラス。
    """
    # -- Model設定 (後から属性の中身が変わってもバリデーションが行われる) --
    model_config = ConfigDict(validate_assignment=True)
    # -- Mapの参照値 --
    nb_drones: int = Field(default=0, gt=0)                                     # ドローン数
    start_zone_name: str = ""                                                   # スタート位置のZone名
    end_zone_name: str = ""                                                     # ゴール位置のZone名
    # -- 管理オブジェクト --
    drones: list[Drone] = Field(default_factory=list)                           # Droneオブジェクトをlistで保存
    zones: dict[str, Zone] = Field(default_factory=dict)                        # Zone名とZoneオブジェクトを辞書で保存
    connections: list[Connection] = Field(default_factory=list)                 # Connerctionオブジェクトをlistで保存
    # -- Other --
    history: list[list[str]] = Field(default_factory=list)                      # 各ターンの出力文字列のリスト
    adjacency_list: dict[str, list[str]] = Field(default_factory=dict)          # 各ゾーンから接続されているゾーン名
    reservation_table: dict[tuple[int, str], int] = Field(default_factory=dict) # 時空間テーブル

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
        self._initialize_zones()
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
        """インスタンス化してスタート地点に全ドローンを配置"""
        for i in range(1, self.nb_drones + 1):
            self.drones.append(Drone(id=f"D{i}",
                               current_location=self.start_zone_name))
            self.zones[self.start_zone_name].can_wait_drone(0)
        # debug mesage
        print(f"{self.nb_drones}機のドローンが {self.start_zone_name} に配置されましたわ！")

    def _initialize_zones(self) -> None:
        """ゾーンの属性の初期化を行う"""
        self.zones[self.start_zone_name].max_drones = self.nb_drones
        self.zones[self.end_zone_name].max_drones = self.nb_drones
        for conn in self.connections:
            self.zones[conn.zone1].connections[conn.zone2] = conn
            self.zones[conn.zone1].neignbors.append(self.zones[conn.zone2])
            self.zones[conn.zone2].connections[conn.zone1] = conn
            self.zones[conn.zone2].neignbors.append(self.zones[conn.zone1])

    # --- シミュレーションメソッド ---
    def simulate(self) -> None:
        """シミュレーションを実行"""
        for drone in self.drones:
            drone.find_shortest_path(self.zones[self.start_zone_name],
                                     self.zones[self.end_zone_name])
        while True:
            if all(not drone.path for drone in self.drones):
                return
            turn_moves = []
            for drone in self.drones:
                move = drone.act()
                if move:
                    turn_moves.append(move)
            self.history.append(turn_moves)

    # --- utiles method ---
    def print_history(self) -> None:
        """記録した履歴を出力"""
        print("\n--- Simulation Output ---")
        for turn in self.history:
            print(" ".join(turn))
        print("-------------------------\n")

    def get_adjacent_zones(self, zone_name: str) -> list[Zone]:
        """指定したゾーンに隣接しているゾーンのリストを返します"""
        return [self.zones[name] for name in self.adjacency_list[zone_name]]

if __name__ == "__main__":
    pass
