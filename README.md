*This project has been created as part of the 42 curriculum by ayhirose.*

# Fly_in

### Description
This is a simulation program that routes multiple drones to their target zones on a given network map in the shortest possible number of turns, without causing collisions or exceeding zone capacities.

Common Objectives
- Create a highly adaptable routing algorithm capable of handling complex maps and constraints.
- Implement a visualizer to clearly display drone behavior.

Personal Objectives
- Ensure robust and versatile module design based on object-oriented programming principles.

Directory Structure
```
.
├── Makefile
├── README.md
├── setup.cfg
├── .gitignore
├── requirements.txt      # Dependencies (pygame, mypy, flake8, etc.)
│
├── fly_in.py             # Entry point
├── model.py              # Data models (Zone, Drone, Network) and core logic
├── utils_io.py           # File I/O utilities
├── parsers.py            # Map data parser
└── visualizer.py         # Terminal output and GUI visualization
```

### Instructions

This program is designed to be executed with **Python 3.10 or higher**

The version at the time of creation is **Python 3.14.3**.

1. **Installation**
```bash
make install
```
Executing this command creates a virtual environment named .venv and installs the packages listed in requirements.txt into it.


**Before execution**, download `maps.tar.gz` and place the extracted folder in the root directory.

2. **Execution**
```bash
make run
```
Uncomment the desired MAP in the Makefile to use it. `01_linear_path` is selected by default.

Alternatively, you can specify the file name by running it manually:
```bash
./.venv/bin/python3 01_linear_path.txt
```
(When running in a way that strictly adheres to the project PDF, please activate the virtual environment beforehand using source .venv/bin/activate. To exit the virtual environment, execute deactivate.)
```bash
sorce .venv/bin/activate
```

3. **Other `Makefile` Commands**
```bash
make lint
make lint-strict
```
Runs static analysis using flake8 and mypy. (-strict runs mypy in strict mode).

```bash
make debug
```
Runs the program using the pdb debugger.

```bash
make clean
```
Deletes cache files.
Executes clean and also removes the .venv virtual environment.

## Additional sections

### algorithm choices and implementation strategy
The algorithm ultimately adopted for cooperative pathfinding in this project is Prioritized Planning (PP) utilizing the Space-Time Dijkstra's Algorithm.

[Evolution from BFS and Its Challenges]
In the early stages of development, implementation started with a simple Breadth-First Search (BFS) that ignored drone interference. Later, I attempted a dynamic recalculation approach: when a collision (zone capacity exceeded) occurred with another drone, that zone was treated as an obstacle, and the path was recalculated.
However, this method had the following fatal flaws:

Inability to evaluate "Waiting": Even in situations where "waiting a few turns would clear the path," BFS could only find spatial detours, resulting in unnecessary long-distance travel.

Lack of cost concept: With the addition of restricted zones that require 2 turns to traverse, BFS, which treats all edge costs as 1, could no longer derive the shortest path.

Chain collisions: Local avoidance maneuvers created new collisions with other drones, risking an infinite loop of recalculations.

[Resolution via Space-Time Dijkstra's Algorithm]
To solve these issues, I expanded the concept to a Space-Time Graph, adding the dimension of "Time" (turns) to the "Space" (X, Y coordinates) graph.
This expansion allowed the algorithm to evaluate the action of "staying in the same zone (waiting)" as a valid movement with a cost of 1.
Each drone registers its movement path in a reservation table (stay data), and subsequent drones calculate their shortest path (minimum turns) using Dijkstra's algorithm while taking into account the future reservation status. This achieved highly efficient routing that flexibly adapts to map topologies and zone restrictions.

**Planning**
- [x] **Phase 1: Foundation**
	- [x] `maps` parser implementation
	- [x] `model.py` class definition
	- [x] Validation implementation
- [x] **Phase 2: Core Logic**
	- [x] Algorithm implementation
- [x] **Phase 3: Application**
	- [x] `visualizer` implementation
- [x] **Phase 4: Packaging**
	- [x] flake8, mypy Pass
	- [x] `Makefile` creation
	- [x] `README` completion

2/20
I spent quite a bit of time on Codexion. But time passes even if I stop, so I must keep moving forward.
A good thing about this compared to Codexion is that it seems to require less studying. There are fewer concepts to understand as prerequisite knowledge, so I can start coding right away.
For now, today I built the data models and introduced the validations I could immediately think of. Using Pydantic as usual. Tomorrow, I'll just check for any omissions and then immediately start creating the parser. Once that's done, I'll move on to the algorithm or the visualizer. In terms of motivation and debugging, should I start with the visualizer?

2/21
Today I implemented the parser. I worked out the specifications in detail during the design phase, so it turned out well. However, if I proceed at this pace, I can't see when it will be finished. I think I've handled the validation well, so I'll leave it at that for now.

2/22
For now, I'll set up an algorithm that goes straight for the shortest path.
Implemented Breadth-First Search (BFS).
I implemented a system where drones move without colliding using BFS. Doing it "without colliding" was really difficult.
Next, I'll incorporate the zone constraints into the BFS algorithm. That'll probably be tomorrow.

2/23
Hmm, this is bad. I implemented the shortest path with BFS, but I'm struggling with processing priority zones and restricted zones.
A complete algorithm overhaul might be necessary.

2/24
Finally decided to introduce the new algorithm.
Things that made me go "Huh?":

The possibility of a zone having multiple types -> Denied.

The main Fly-in algorithm is complete.
...I think. At least it cleared all the benchmark turn counts for the subject maps.
It's apparently called the "Space-Time Dijkstra's Algorithm". Tickles my inner edge-lord.
Remaining tasks:

Refine validations

Introduce the visualizer

Auto-calculate and output secondary performance metrics

2/26
My days and nights are reversed, so the dates are skipping.
The algorithm is done, so I'll make it output in color.
Terminal visualizer module complete.
Tomorrow is probably GUI.

2/28
Dates skipped again. Seems like I'm only making progress every other day, so I might be mysteriously slacking off.
GUI implementation. I did a major overhaul of the class design, changing it from a class-method type to an instance type.
For now, most of the work is done. All that's left is formatting and error handling.

3/1
Oh no, I slacked off too much.
Let's get it into a submittable state. Then tidy up Codexion, and submit the day after tomorrow.

### visualize
1. Terminal Console Output (CUI):
The progress of the simulation is output to the terminal in vivid colored text using ANSI escape sequences. Not only can you quickly check the exact movement of the drones for each turn via text, but after the simulation is complete, secondary performance metrics such as "total turns" and "movement efficiency per turn" are automatically calculated and output. This allows for an objective evaluation of the algorithm's efficiency.

2. Graphical User Interface (GUI):
The pygame library is used to graphically animate the movement of the drones.

Intuitive Map Comprehension: Zone types (Normal, Restricted, Priority, Blocked) are visually distinguished by shape (circle, square, diamond, cross).

Time Travel Feature: You can freely advance or rewind turns using the left and right arrow keys, allowing for detailed analysis of whether traffic jams occurred on specific turns.

Capacity (Analysis) Mode: Pressing the TAB key activates a hidden mode where the maximum capacity of each zone floats up like a hologram, allowing visual confirmation of the network's limits.

### Resources

AI (Gemini)
- Model design
- Error log analysis
- Docstring creation
