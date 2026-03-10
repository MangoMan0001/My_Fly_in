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


*This project has been created as part of the 42 curriculum by ayhirose.*

# Fly_in

### Description
与えられたネットワークマップ上で、複数のドローンを衝突やキャパシティオーバーを起こすことなく、最短ターン数で目的のゾーンへルーティングするシミュレーションプログラムです。

共通目標
- 適応性の高いルーティングアルゴリズムの作成
- ドローン挙動のVisualizerを作成する。

個人目標
- 汎用性のあるモジュール設計にする

ディレクトリ構成
```
.
├── Makefile
├── README.md
├── setup.cfg
├── .gitignore
├── requirements.txt      # 依存ライブラリ（pygame, mypy, flake8等）
│
├── fly_in.py             # エントリーポイント
├── model.py              # データモデル（Zone, Drone, Network）とコアロジック
├── utils_io.py           # ファイル読み込みユーティリティ
├── parsers.py            # マップデータの構文解析（パーサー）
└── visualizer.py         # ターミナル出力およびGUIによる可視化
```

### Instructions

プログラムは**Python 3.10以上**での実行が前提で作成されています。

1. **インストール**
```bash
make install
```
このコマンドを実行すると`.venv`という名前で仮想環境が構築され、`requirement.txt`に記述されたパッケージを`.venv`にインストールされます。

2. **プログラムの実行**
```bash
make run
```
Makefile内で使用したいMAPをコメント解除して使用してください。初期は`01_linear_path`が選択されています。

```bash
./.venv/bin/python3 01_linear_path.txt
```
また、手動で実行することでファイル名を指定することも可能です。
```bash
sorce .venv/bin/activate
```
課題pdfに準拠する形で実行する場合は、事前に仮想環境を`activate`してください。 \
仮想環境から離脱する場合は`deactivate`を実行してください。

3. **その他の`Makefile`コマンド**
```bash
make lint
make lint-strict
```
静的解析: `flake8` と `mypy`を実行。 \
`-strict`でstrictモードで実行

```bash
make debug
```
デバッグモード: `pdb`を使用して実行。

```bash
make clean
```
クリーンアップ: キャッシュファイルの削除。 \
`fclean`で`.venv`も削除。


## Additional sections

### algorithm choices and implementation strategy
本プロジェクトにおいて、協調経路探索として最終的に採用したアルゴリズムは 時空間ダイクストラ法（Space-Time Dijkstra's Algorithm） を用いた Prioritized Planning (PP) です。

【BFSからの変遷と課題】
開発の初期段階では、ドローンの干渉を無視したシンプルな幅優先探索（BFS）から実装をスタートしました。その後、他機との衝突（ゾーンのキャパシティ超過）が発生した際に、そのゾーンを障害物とみなして再探索するという動的再計算のアプローチを試みました。
しかし、この手法には以下の致命的な欠陥がありました。

「待機」の評価不可: 「数ターン待てば道が空く」という状況でも、BFSは空間的な迂回ルートしか見つけることができず、無駄な長距離移動が発生してしまう。

コスト概念の欠如: 移動に2ターンかかる制限ゾーン（restricted）が追加されたことで、すべてのエッジのコストを1として扱うBFSでは最短経路が導き出せなくなった。

連鎖的な衝突: 局所的な回避行動が別のドローンとの新たな衝突を生み、再計算の無限ループに陥る危険性があった。

【時空間ダイクストラ法による解決】
これらの問題を解決するため、X座標・Y座標という「空間」のグラフに、ターン数という「時間」の次元を加えた 時空間（Space-Time）グラフ へと概念を拡張しました。
この拡張により、「同じゾーンに留まる（待機する）」という行動をコスト1の正当な移動としてアルゴリズムに評価させることが可能になりました。
各ドローンは自身の移動経路を予約表（滞在データ）に登録し、後続のドローンはその未来の予約状況を加味した上でダイクストラ法による最短経路（最短ターン数）を計算します。これにより、マップのトポロジーやゾーンの制限に柔軟に適応する、極めて効率的なルーティングを実現しました。

**Planning**
-  [x]  **Phase 1: 基盤作成**
    - [x] `maps`パーサー実装
    - [x] `model.py`クラス定義
    	- [x] バリデーション導入
- [x] **Phase 2: コアロジック**
    - [x]  アルゴリズムの実装
- [x] **Phase 3: アプリケーション**
    - [x] `visualizer` の実装
- [ ] **Phase 4: パッケージ化**
    - [ ] flake8, mypyのPass
    - [ ] `Makefile`の作成
    - [ ] `README`の完成

2/20 \
Codexionにかなり時間をかけてしまった。 \
だからといって立ち止まっても時は過ぎるので、前進あるのみ。 \
Codexionよりいいことは座学が少なくて済みそうだということ。理解すべき概念が事前知識として少ないのですぐにでもコードに取り掛かれる。 \
とりあえず今日はデータモデルの構築とパッと思いつくバリデーションを導入した。例によってPydantic、明日は漏れがないかだけ見て、早速パーサー作成に入ろうと思う。それができたらアルゴリズムかヴィジュアライズに移る。モチベとデバッグ的にはヴィジュアライズから入るべきか？

2/21 \
今日はパーサーを実装した。かなり設計から細かく仕様を練ったので、出来はいい。が、この調子で進むといつ完成するのか先は見えない。バリデーションもこなせていると思うので、とりあえずはよしとするか

2/22 \
とりあえずは最短経路を一直線に進むアルゴリズムを設けようと思う \
幅優先探索を実装した。 \
幅優先探索で、ドローンが衝突せずに移動する仕組みを実装した。衝突せずにというのが本当に難しかった。 \
これからゾーンの縛りを幅優先探索アルゴリズムに落とし込んでいく。それは明日かな

2/23 \
うーんまずい。最短経路をBFSで実装したが、優先ゾーンや制限ゾーンの処理に手こずるぞ。 \
アルゴリズム一新が必要になるかもしれん

2/24 \
ついに新アルゴリズムの導入に踏み切る \
あれっ？って思う内容
- ゾーンがタイプを複数持つ可能性　→ 否定されました

Fly-inメインアルゴリズムが完成した。 \
…はず、一応課題マップの基準ターン数は全てクリア \
時空間ダイクストラ法という名前らしい。厨二心 \
残すタスクは
- バリデーションを詰める
- ヴィジュアライザの導入
- ２次評価基準の自動計算と出力

2/26 \
昼夜逆転してるので日付が飛ぶ \
アルゴリズムは完成しているのでそれを色付き出力にする。 \
ターミナルヴィジュアライザーモジュール完成 \
明日はGUIかな

2/28 \
またも日付が飛んだ。二日に一回しか進んでないみたいで謎にサボってそう。 \
GUI実装。一回クラスの設計をクラスメソッド型からインスタンス型に大幅チェンジした。 \
ひとまずおおかたの作業は終えた。あとは形を整えていく作業と、エラーハンドリングだ。


3/1 \
まずいサボりすぎた \
出せる形にしよう。そしてCodexionも整えて、明後日提出だ。

### visualize
Terminal Console Output (CUI):
シミュレーションの進行状況を、ANSIエスケープシーケンスを用いた鮮やかな色付きテキストでターミナルに出力します。各ターンごとのドローンの正確な動きをテキストベースで素早く確認できるだけでなく、シミュレーション完了後には「総ターン数」や「1ターンあたりの移動効率」などの二次評価基準（Performance Metrics）を自動計算して出力し、アルゴリズムの効率性を客観的に評価できるようにしています。

Graphical User Interface (GUI):
pygame ライブラリを使用し、ドローンの移動をグラフィカルにアニメーション表示します。

- 直感的なマップ把握: ゾーンの種類（Normal, Restricted, Priority, Blocked）を形状（円、四角、ひし形、バツ印）で視覚的に区別。

- タイムトラベル機能: 左右の矢印キーでターンを自由に進めたり戻したりすることができ、特定のターンで渋滞が起きていないか詳細な分析が可能です。

- キャパシティ（解析）モード: TABキーを押すことで、各ゾーンの上限キャパシティがホログラムのように浮かび上がる裏モードを搭載し、ネットワークの限界値を視覚的に確認できるようにしています。

### Resources

AI (Gemini)
- Model設計
- エラーログの解析
- Docstring作成
