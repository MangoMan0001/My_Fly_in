#!/usr/bin/env python3
"""Main entry point for the drone network simulation."""

import argparse
from utils_io import read_text_file
from parsers import DroneNetworkParser
from visualizer import ConsoleVisualizer, GraphicVisualizer


def get_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        argparse.Namespace: parsed arguments containing the input file path.
    """
    parser = argparse.ArgumentParser(description="Drone Network Simulation")
    parser.add_argument("input_file", type=str, help="Path to the input_file")
    return parser.parse_args()


def main() -> None:
    """Run the main simulation flow.

    This function reads the map file, parses the network, executes
    the routing simulation, and launches the visualizers.
    """
    args = get_args()
    text_data = read_text_file(args.input_file)

    parser = DroneNetworkParser()
    network = parser.parse(text_data)
    print(f"Parsed successfully! Number of drones: {network.nb_drones}")

    network.simulate()

    ConsoleVisualizer.render_method(network)
    visualizer = GraphicVisualizer(1280, 720)
    visualizer.rend_gui(network, args.input_file)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
