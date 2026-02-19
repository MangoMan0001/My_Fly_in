#!/usr/bin/env python3

from enum import Enum
from typing import Optional
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

    # 名前に「- (ダッシュ)」 か 「' '(スペース)」が含まれていないかチェック
    @field_validator('name')
    @classmethod
    def name_must_not_contain_dash_space(cls, v: str) -> str:
        if '-' in v:
            raise ValueError("Zone name cannot contain dashes")
        if ' ' in v:
            raise ValueError("Zone name cannot contain space")
        return v

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

# --- 3. DroneNetwork (統括) モデル ---
class DroneNetwork(BaseModel):
    """
    ドローンネットワーク全体を管理する司令塔クラス。
    """
    model_config = ConfigDict(validate_assignment=True)
    nb_drones: int = Field(..., gt=0)

    zones: dict[str, Zone] = Field(default_factory=dict)
    connections: list[Connection] = Field(default_factory=list)

    start_zone_name: Optional[str] = None
    end_zone_name: Optional[str] = None

    def validate_network_integrity(self) -> None:
        """
        パース完了後に、ネットワーク全体に矛盾がないかチェック
        """
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

            # 3. 重複チェック (A-B と B-A を同じものとして扱うためにソートしてタプルにしますわ)
            edge = tuple(sorted([conn.zone1, conn.zone2]))
            if edge in seen_connections:
                raise ValueError(f"Duplicate connection detected: {conn.zone1}-{conn.zone2}")
            seen_connections.add(edge)

    def add_zone(self, zone: Zone) -> None:
        if zone.name in self.zones:
            raise ValueError(f"Duplicate zonename detected: {zone.name}")
        for existing_zone in self.zones.values():
            if existing_zone.x == zone.x and existing_zone.y == zone.y:
                raise ValueError(f"Coordinate overlap detected: {zone.name} "
                                 f"and {existing_zone.name} are at ({zone.x}, {zone.y})")
        self.zones[zone.name] = zone

    def add_start_zone(self, zone: Zone) -> None:
        if self.start_zone_name is not None:
            raise ValueError(f"two or more startzone settings detected: {zone.name}")
        self.add_zone(zone)
        self.start_zone_name = zone.name

    def add_end_zone(self, zone: Zone) -> None:
        if self.end_zone_name is not None:
            raise ValueError(f"two or more endtzone settings detected: {zone.name}")
        self.add_zone(zone)
        self.end_zone_name = zone.name

    def add_connection(self, connection: Connection) -> None:
        if not connection.zone1 in self.zones or not connection.zone2 in self.zones:
            raise ValueError(f"Connection to an undefined zone detected: {connection.zone1}-{connection.zone2}")
        self.connections.append(connection)

    def get_adjacent_zones(self, zone_name: str) -> list[Zone]:
        """
        指定したゾーンに隣接している（移動可能な）ゾーンのリストを返しますわ。
        ※経路探索で頻繁に使うことになる重要なメソッドですわね！
        """
        return []

    def initialize_drones(self) -> None:
        """
        シミュレーション開始前に、指定された数のドローンを start_zone に配置しますわ。
        """
        pass

    def simulate_step(self) -> None:
        """
        1ターンのシミュレーションを進めますわ。
        全ドローンの移動計画を立て、競合がないか確認し、移動を実行しますの。
        """
        pass

if __name__ == "__main__":
    pass
