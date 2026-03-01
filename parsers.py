#!/usr/bin/env python3
"""Module for parsing drone network data."""

from model import Zone, Connection, DroneNetwork
from typing import Any


class DroneNetworkParser:
    """Parser for drone network text data."""

    def parse(self, input_text: str) -> DroneNetwork:
        """Parse the input string and build a DroneNetwork model.

        Args:
            input_text (str): The raw text data defining the network.

        Returns:
            DroneNetwork: The fully initialized drone network.

        Raises:
            ValueError: If the input format violates the specified constraints.
        """
        lines = input_text.strip().split('\n')
        network = DroneNetwork()

        for row, line in enumerate(lines, 1):
            try:
                if not line or line.startswith('#'):
                    continue

                if line.startswith("nb_drones:"):
                    if 0 < network.nb_drones:
                        raise ValueError("nb_drones is defined twice.")
                    if network.zones or network.connections:
                        raise ValueError(
                            "nb_drones is not defined in the first line."
                        )
                    network.nb_drones = self._nb_parse(line)
                    continue
                # .行の後ろにあるコメントを削除
                clean_line = line.split('#', 1)[0].strip()

                if line.startswith("start_hub:"):
                    network.add_start_zone(self._zone_parse(clean_line))
                    continue

                if line.startswith("end_hub:"):
                    network.add_end_zone(self._zone_parse(clean_line))
                    continue

                if line.startswith("hub:"):
                    network.add_zone(self._zone_parse(clean_line))
                    continue

                if line.startswith("connection:"):
                    network.add_connection(self._connection_parse(clean_line))
                    continue

                raise ValueError(
                    "This format differs from the specified constraints."
                    )

            except ValueError as e:
                raise ValueError(
                    f"Parsing error at line {row}: {e}\n  -> {line}"
                    )

        network.initialize()

        return network

    def _nb_parse(self, line: str) -> int:
        """Parse the nb_drones line.

        Args:
            line (str): The line containing the number of drones.

        Returns:
            int: The parsed number of drones.
        """
        return int(line.split(':', 1)[1].strip())

    def _zone_parse(self, line: str) -> Zone:
        """Parse a zone definition line.

        Args:
            line (str): The line defining a zone.

        Returns:
            Zone: A new Zone object with extracted properties and metadata.

        Raises:
            ValueError: If the zone definition format is invalid.
        """
        data = line.split(':', 1)[1].strip()

        # 1.[]に囲われたメタデータとそれ以外に分ける
        if '[' in data and ']' in data:
            main, meta = data.split('[', 1)
            meta_data = meta.replace(']', '').strip()
            main_data = main.strip()
        else:
            meta_data = ""
            main_data = data

        # 2.name, x, yを抽出
        main_list = main_data.split()
        if len(main_list) != 3:
            raise ValueError(f"Zone definition is invalid: {main_data}")
        name = main_list[0]
        x = int(main_list[1])
        y = int(main_list[2])

        # 3.メタデータを辞書にする
        meta_dict: dict[str, Any] = {}
        if meta_data:
            meta_list = meta_data.split()
            for meta in meta_list:
                key, value = meta.split('=', 1)
                if key == "zone":
                    meta_dict["zone_type"] = value
                elif key == "max_drones":
                    meta_dict[key] = int(value)
                else:
                    meta_dict[key] = value

        return Zone(name=name, x=x, y=y, **meta_dict)

    def _connection_parse(self, line: str) -> Connection:
        """Parse a connection definition line.

        Args:
            line (str): The line defining a connection between two zones.

        Returns:
            Connection: A new Connection object with extracted properties.

        Raises:
            ValueError: If the connection definition format is invalid.
        """
        data = line.split(':', 1)[1].strip()

        # 1.[]に囲われたメタデータとそれ以外に分ける
        if '[' in data and ']' in data:
            main, meta = data.split('[', 1)
            meta_data = meta.replace(']', '').strip()
            main_data = main.strip()
        else:
            meta_data = ""
            main_data = data

        # 2.zone1, zone2を抽出
        main_list = main_data.split('-', 1)
        if len(main_list) != 2:
            raise ValueError(f"Connection definition is invalid: {main_data}")
        zone1, zone2 = main_list

        # 3.メタデータを辞書にする
        meta_dict: dict[str, Any] = {}
        if meta_data:
            meta_list = meta_data.split()
            for meta in meta_list:
                key, value = meta.split('=', 1)
                meta_dict[key] = int(value)

        return Connection(
            name=main_data, zone1=zone1, zone2=zone2, **meta_dict
            )


if __name__ == "__main__":
    pass
