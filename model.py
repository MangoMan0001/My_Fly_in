#!/usr/bin/env python3
"""Module defining the data models and core simulation logic."""

from enum import Enum
from typing import Optional
from collections import deque
import heapq
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    ConfigDict
)


# --- 1. Define allowed zone types ---
class ZoneType(str, Enum):
    """Enumeration of allowed zone types in the network."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


# --- 2. Zone (Node) Model ---
class Zone(BaseModel):
    """Model representing a single zone (node) in the network."""

    name: str
    x: int
    y: int

    zone_type: ZoneType = Field(default=ZoneType.NORMAL)
    color: Optional[str] = Field(default=None)
    max_drones: int = Field(default=1, gt=0)

    # Space-time data [turn: drone_count]
    parking_drones: dict[int, int] = Field(default_factory=dict)
    # Connected edges [zone_name: Connection]
    connections: dict[str, 'Connection'] = Field(default_factory=dict)
    # Neighboring zones
    neighbors: list['Zone'] = Field(default_factory=list)

    @field_validator('name')
    @classmethod
    def name_must_not_contain_dash_space(cls, v: str) -> str:
        """Ensure the zone name does not contain dashes or spaces.

        Args:
            v (str): The proposed zone name.

        Returns:
            str: The validated zone name.

        Raises:
            ValueError: If the name contains a dash or a space.
        """
        if '-' in v:
            raise ValueError("Zone name cannot contain dashes")
        if ' ' in v:
            raise ValueError("Zone name cannot contain space")
        return v

    def can_accept_drone(self, turn: int, zone: 'Zone') -> bool:
        """Check if the zone can accept a drone at the specified turn.

        Args:
            turn (int): The simulation turn to check.
            zone (Zone): The previous zone the drone is coming from.

        Returns:
            bool: True if the zone can accept the drone, False otherwise.
        """
        if self.zone_type == ZoneType.BLOCKED:
            return False
        conn = self.connections[zone.name]
        if self.parking_drones.get(turn, 0) < self.max_drones:
            return conn.can_connect_drone(turn)
        return False

    def can_wait_drone(self, turn: int) -> bool:
        """Check if a drone can wait in this zone for one turn.

        Args:
            turn (int): The simulation turn to check.

        Returns:
            bool: True if waiting is allowed, False otherwise.
        """
        if self.zone_type == ZoneType.BLOCKED:
            return False
        if self.parking_drones.get(turn, 0) < self.max_drones:
            return True
        return False

    def add_drone(self, turn: int, zone: 'Zone') -> None:
        """Add a drone to this zone at the specified turn.

        Args:
            turn (int): The simulation turn.
            zone (Zone): The previous zone the drone is coming from.

        Raises:
            ValueError: If the zone is already at maximum capacity.
        """
        conn = self.connections[zone.name]
        if not self.can_accept_drone(turn, zone):
            raise ValueError("The zone is already at maximum capacity")
        conn.connect_drone(turn)
        self.parking_drones[turn] = self.parking_drones.get(turn, 0) + 1

    def wait_drone(self, turn: int) -> None:
        """Make a drone wait in this zone at the specified turn.

        Args:
            turn (int): The simulation turn.

        Raises:
            ValueError: If the zone is already at maximum capacity.
        """
        if not self.can_wait_drone(turn):
            raise ValueError("The zone is already at maximum capacity")
        self.parking_drones[turn] = self.parking_drones.get(turn, 0) + 1

    def get_cost(self) -> int:
        """Get the movement cost required to enter this zone.

        Returns:
            int: 2 if the zone is restricted, otherwise 1.
        """
        if self.zone_type == ZoneType.RESTRICTED:
            return 2
        return 1


# --- 3. Connection (Edge) Model ---
class Connection(BaseModel):
    """Model representing an edge connecting two zones."""

    name: str
    zone1: str
    zone2: str
    max_link_capacity: int = Field(default=1, gt=0)
    # Space-time data [turn: drone_count]
    parking_drones: dict[int, int] = Field(default_factory=dict)

    # 自分自身との接続を弾く
    @model_validator(mode='after')
    def check_zones_are_different(self) -> 'Connection':
        """Ensure that a connection does not link a zone to itself.

        Returns:
            Connection: The validated connection instance.

        Raises:
            ValueError: If zone1 and zone2 are identical.
        """
        if self.zone1 == self.zone2:
            raise ValueError(f"A zone cannot connect to itself: {self.zone1}")
        return self

    def can_connect_drone(self, turn: int) -> bool:
        """Check if a drone can use this connection at a given turn.

        Args:
            turn (int): The simulation turn to check.

        Returns:
            bool: True if the connection is available, False otherwise.
        """
        if self.parking_drones.get(turn, 0) < self.max_link_capacity:
            return True
        return False

    def connect_drone(self, turn: int) -> None:
        """Register a drone passing through this connection.

        Args:
            turn (int): The simulation turn.

        Raises:
            ValueError: If the connection is at maximum capacity.
        """
        if not self.can_connect_drone(turn):
            raise ValueError("The connection is at maximum capacity")
        self.parking_drones[turn] = self.parking_drones.get(turn, 0) + 1


# --- 4. Drone モデル ---
class Drone(BaseModel):
    """Class managing a single drone's state and pathfinding."""

    id: str
    path: deque[str] = Field(default_factory=deque)
    total_cost: int = 0

    def act(self) -> str:
        """Execute one turn of movement for the drone.

        Returns:
            str: The movement formatted string, or empty if waiting/done.
        """
        if not self.path:
            return ""
        move = self.path.popleft()
        if move == "Wa-it":
            return ""
        return f"{self.id}-{move}"

    def find_shortest_path(
        self,
        start_zone: Zone,
        target_zone: Zone,
        zones: dict[str, Zone]
    ) -> None:
        """Find the shortest path using space-time Dijkstra's algorithm.

        Args:
            start_zone (Zone): The starting location.
            target_zone (Zone): The destination location.
            zones (dict[str, Zone]): Dictionary mapping names to Zone objects.
        """
        # キューに入れるデータ: (総ターン数, -優先ゾーン通過数, 現在のゾーン, 経路のリスト)
        queue: list[tuple[int, int, str, Zone, list[str]]] = []
        heapq.heappush(queue, (0, 0, start_zone.name,
                               start_zone, [start_zone.name]))

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
                self.path = deque(path[1:])
                self.total_cost = len(self.path)
                zone = start_zone
                for turn, name in enumerate(self.path, 1):
                    if name == "Wa-it":
                        zone.wait_drone(turn)
                    elif '-' in name:
                        continue
                    elif zones[name].zone_type == ZoneType.RESTRICTED:
                        zone.connections[name].connect_drone(turn - 1)
                        zones[name].add_drone(turn, zone)
                        zone = zones[name]
                    else:
                        zones[name].add_drone(turn, zone)
                        zone = zones[name]
                return

            # 待機できるならキューに追加
            if current.can_wait_drone(cost + 1):
                heapq.heappush(
                    queue,
                    (cost + 1, priority, current.name,
                     current, path + ["Wa-it"])
                )
            # 隣接ゾーンへ移動
            for neighbor in current.neighbors:
                if neighbor.zone_type == ZoneType.PRIORITY:
                    priority -= 1

                if neighbor.zone_type == ZoneType.RESTRICTED:
                    conn = neighbor.connections[current.name]
                    if not conn.can_connect_drone(cost + 1):
                        continue
                    if neighbor.can_accept_drone(cost + 2, current):
                        turn_path = [conn.name] + [neighbor.name]
                        heapq.heappush(
                            queue,
                            (cost + 2, priority, neighbor.name,
                             neighbor, path + turn_path)
                        )
                    continue

                if neighbor.can_accept_drone(cost + 1, current):
                    heapq.heappush(
                        queue,
                        (cost + 1, priority, neighbor.name,
                         neighbor, path + [neighbor.name])
                    )


# --- 5. DroneNetwork Model ---
class DroneNetwork(BaseModel):
    """The central class that manages the entire drone network."""

    model_config = ConfigDict(validate_assignment=True)
    # -- Mapの参照値 --
    nb_drones: int = Field(default=0, gt=0)
    start_zone_name: str = ""
    end_zone_name: str = ""
    # -- 管理オブジェクト --
    drones: list[Drone] = Field(default_factory=list)
    zones: dict[str, Zone] = Field(default_factory=dict,
                                   description="zone_name:zone")
    connections: list[Connection] = Field(default_factory=list)
    # -- Other --
    history: list[list[str]] = Field(default_factory=list,
                                     description="各ターンの出力文字列のリスト")
    adjacency_list: dict[str, list[str]] = Field(
        default_factory=dict, description="各ゾーンから接続されているゾーン名"
        )

    # --- Setter Method ---
    def add_zone(self, zone: Zone) -> None:
        """Add a new zone to the network.

        Args:
            zone (Zone): The zone object to add.

        Raises:
            ValueError: If a duplicate name or overlapping coordinates exist.
        """
        if zone.name in self.zones:
            raise ValueError(f"Duplicate zonename detected: {zone.name}")
        for existing_zone in self.zones.values():
            if existing_zone.x == zone.x and existing_zone.y == zone.y:
                raise ValueError(
                    f"Coordinate overlap detected: {zone.name} "
                    f"and {existing_zone.name} are at ({zone.x}, {zone.y})"
                )
        self.zones[zone.name] = zone

    def add_start_zone(self, zone: Zone) -> None:
        """Register the starting zone of the network.

        Args:
            zone (Zone): The start zone object.

        Raises:
            ValueError: If a start zone has already been defined.
        """
        if self.start_zone_name:
            raise ValueError(
                f"Two or more start zone settings detected: {zone.name}"
            )
        self.add_zone(zone)
        self.start_zone_name = zone.name

    def add_end_zone(self, zone: Zone) -> None:
        """Register the ending (target) zone of the network.

        Args:
            zone (Zone): The end zone object.

        Raises:
            ValueError: If an end zone has already been defined.
        """
        if self.end_zone_name:
            raise ValueError(
                f"Two or more end zone settings detected: {zone.name}"
            )
        self.add_zone(zone)
        self.end_zone_name = zone.name

    def add_connection(self, connection: Connection) -> None:
        """Add a connection between two zones.

        Args:
            connection (Connection): The connection object.

        Raises:
            ValueError: If the connection references undefined zones.
        """
        if (connection.zone1 not in self.zones or
                connection.zone2 not in self.zones):
            raise ValueError(
                "Connection to an undefined zone detected: "
                f"{connection.zone1}-{connection.zone2}"
            )
        self.connections.append(connection)

    # --- Initialize and Validation Method ---
    def initialize(self) -> None:
        """Initialize and validate the network before simulation."""
        self._validate_network_integrity()
        self._build_adjacent_zones()
        self._initialize_zones()
        self._initialize_drones()
        self._pre_bfs()

    def _validate_network_integrity(self) -> None:
        """Check the overall integrity of the parsed network structure.

        Raises:
            ValueError: If there are missing hubs or duplicated edges.
        """
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
                raise ValueError(
                    "Connection links to undefined zones: "
                    f"{conn.zone1}-{conn.zone2}"
                )

            # 3. 重複チェック
            edge = tuple(sorted([conn.zone1, conn.zone2]))
            if edge in seen_connections:
                raise ValueError(
                    "Duplicate connection detected: "
                    f"{conn.zone1}-{conn.zone2}"
                )
            seen_connections.add(edge)

        # 4. nb_droneが設定されているかチェック
        if not self.nb_drones:
            raise ValueError("The nb_drone is not configured.")

    def _build_adjacent_zones(self) -> None:
        """Build an adjacency list linking zones to their neighbors."""
        for name in self.zones:
            self.adjacency_list[name] = []
        for conn in self.connections:
            self.adjacency_list[conn.zone1].append(conn.zone2)
            self.adjacency_list[conn.zone2].append(conn.zone1)

    def _initialize_drones(self) -> None:
        """Instantiate all drones and place them in the start zone."""
        for i in range(1, self.nb_drones + 1):
            self.drones.append(Drone(id=f"D{i}"))
            self.zones[self.start_zone_name].can_wait_drone(0)

        print(f"Successfully deployed {self.nb_drones} drones "
              f"at {self.start_zone_name}!")

    def _initialize_zones(self) -> None:
        """Set up initial capacities and neighbor links for all zones."""
        self.zones[self.start_zone_name].max_drones = self.nb_drones
        self.zones[self.end_zone_name].max_drones = self.nb_drones
        for conn in self.connections:
            self.zones[conn.zone1].connections[conn.zone2] = conn
            self.zones[conn.zone1].neighbors.append(self.zones[conn.zone2])
            self.zones[conn.zone2].connections[conn.zone1] = conn
            self.zones[conn.zone2].neighbors.append(self.zones[conn.zone1])

    def _pre_bfs(self) -> None:
        """Check if there is a route available."""
        queue = deque([self.zones[self.start_zone_name]])
        history: set[str] = set()
        if self.zones[self.start_zone_name].zone_type == ZoneType.BLOCKED:
            raise ValueError("Map data cannot reach the end_hub.")
        while queue:
            current = queue.popleft()
            if current.name in history:
                continue
            history.add(current.name)
            if current.name == self.end_zone_name:
                return
            for zone_name in self.adjacency_list[current.name]:
                if self.zones[zone_name].zone_type == ZoneType.BLOCKED:
                    continue
                queue.append(self.zones[zone_name])
        raise ValueError("Map data cannot reach the end_hub.")

    # --- シミュレーションメソッド ---
    def simulate(self) -> None:
        """Run the simulation until all drones reach their destination."""
        for drone in self.drones:
            drone.find_shortest_path(
                self.zones[self.start_zone_name],
                self.zones[self.end_zone_name],
                self.zones
            )
        count = 0
        while True:
            if all(not drone.path for drone in self.drones):
                return
            turn_moves = []
            for drone in self.drones:
                move = drone.act()
                if move:
                    turn_moves.append(move)
            self.history.append(turn_moves)
            count += 1

    # --- utiles method ---
    def print_history(self) -> None:
        """Print the recorded simulation history to the terminal."""
        print("\n--- Simulation Output ---")
        for turn in self.history:
            print(" ".join(turn))
        print("-------------------------\n")


if __name__ == "__main__":
    pass
