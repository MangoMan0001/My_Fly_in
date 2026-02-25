*This project has been created as part of the 42 curriculum by ayhirose.*

# Fly_in

### Description
Pythonベースのドローンの同時操作アルゴリズム

共通目標
- 適応性の高いアルゴリズムを作成する。
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
│
├── requirements.txt                    # 依存ライブラリ（mlx, mypy, flake8等）
├── parsers.py		                    # マップ読み込み
└── model.py							# データモデル
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
`fclean`で`.venv`と`maze.txt`も削除。


## Additional sections

### algorithm choices

### implementation strategy

**Planning**
-  [ ]  **Phase 1: 基盤作成**
    - [x] `maps`パーサー実装
    - [ ] `model.py`クラス定義
    	- [x] バリデーション導入
- [ ] **Phase 2: コアロジック**
    - [ ]  アルゴリズムの実装
- [ ] **Phase 3: アプリケーション**
    - [ ] `visualizer` の実装
- [ ] **Phase 4: パッケージ化**
    - [ ] flake8, mypyのPass
    - [ ] `Makefile`の作成
    - [ ] `README`の完成

2/20

Codexionにかなり時間をかけてしまった。余裕はなく、常に焦燥感に駆られている。

だからといって立ち止まっても時は過ぎるので、前進あるのみである。

Codexionよりいいことは座学が少なくて済みそうだということ。理解すべき概念が事前知識として少ないのですぐにでもコードに取り掛かれる。

とりあえず今日はデータモデルの構築とパッと思いつくバリデーションを導入した。例によってPydanticである。明日は漏れがないかだけ見て、早速パーサー作成に入ろうと思う。それができたらアルゴリズムかヴィジュアライズに移る。モチベとデバッグ的にはヴィジュアライズから入るべきだろう。

2/21

今日はパーサーを実装した。かなり設計から細かく仕様を練ったので、出来はいい。

が、この調子で進むといつ完成するのか先は見えない。バリデーションもこなせていると思うので、とりあえずはよしとするか

2/22
とりあえずは最短経路を一直線に進むアルゴリズムを設けようと思う

幅優先探索を実装した。

幅優先探索で、ドローンが衝突せずに移動する仕組みを実装した。衝突せずにというのが本当に難しかった。

これからゾーンの縛りを幅優先探索アルゴリズムに落とし込んでいく。それは明日かな

2/23
うーんまずい。最短経路をBFSで実装したが、優先ゾーンや制限ゾーンの処理に手こずるぞ。
アルゴリズム一新が必要になるかもしれん

### visualize

### Resources

AI (Gemini)
- Model設計
- エラーログの解析
- Docstring作成
