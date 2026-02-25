# ==========================================
#  Fly_in Project Makefile
# ==========================================

# 実行するPythonコマンド
PYTHON_EXEC = python3.14

# プロジェクト名とメインスクリプト
NAME        = fly_in
MAIN_SCRIPT = fly_in.py
# MAP_FILE = ../pdf/maps/easy/01_linear_path.txt
# MAP_FILE = ../pdf/maps/easy/02_simple_fork.txt
# MAP_FILE = ../pdf/maps/easy/03_basic_capacity.txt
# MAP_FILE = ../pdf/maps/medium/01_dead_end_trap.txt
# MAP_FILE = ../pdf/maps/medium/02_circular_loop.txt
# MAP_FILE = ../pdf/maps/medium/03_priority_puzzle.txt
# MAP_FILE = ../pdf/maps/hard/01_maze_nightmare.txt
# MAP_FILE = ../pdf/maps/hard/02_capacity_hell.txt
# MAP_FILE = ../pdf/maps/hard/03_ultimate_challenge.txt
MAP_FILE = ../pdf/maps/challenger/01_the_impossible_dream.txt

# 仮想環境の設定
VENV        = .venv
PYTHON      = $(VENV)/bin/python3
PIP         = $(VENV)/bin/pip
PY_VERSION  = python3

# 依存パッケージ
REQUIREMENTS = requirements.txt

# lint option
MYPY_OPTION = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

# ==========================================
#  Rules
# ==========================================

.PHONY: all install run debug clean lint lint-strict build re

all: install

# ------------------------------------------
#  Environment Setup
# ------------------------------------------
install: ## 仮想環境を作成し、依存関係をインストールする
	@echo "Creating virtual environment..."
	$(PY_VERSION) -m venv $(VENV)
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r $(REQUIREMENTS)
	@echo "Setup complete! Run 'make run' to start."

# ------------------------------------------
#  Execution
# ------------------------------------------
run: ## メインプログラムを実行
	@echo "Running $(NAME)..."
	@if [ ! -d "$(VENV)" ]; then echo "Venv not found. Run 'make install' first."; exit 1; fi
	@$(PYTHON) $(MAIN_SCRIPT) $(MAP_FILE)

debug: ## pdbデバッガを使って実行
	@echo "Debugging $(NAME)..."
	@if [ ! -d "$(VENV)" ]; then echo "Venv not found. Run 'make install' first."; exit 1; fi
	@$(PYTHON) -m pdb $(MAIN_SCRIPT) $(MAP_FILE)

# ------------------------------------------
#  Quality Control
# ------------------------------------------
lint: ## Flake8とMypyによる静的解析を実行
	@echo "Running Linter (Standard)..."
	@if [ ! -d "$(VENV)" ]; then echo "Venv not found. Run 'make install' first."; exit 1; fi
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy $(MYPY_OPTION) .

lint-strict: ## より厳しいMypyチェックを実行
	@echo "Running Linter (Strict)..."
	@if [ ! -d "$(VENV)" ]; then echo "Venv not found. Run 'make install' first."; exit 1; fi
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict

# ------------------------------------------
#  Cleanup
# ------------------------------------------
clean: ## 一時ファイルやキャッシュを削除
	@echo "Cleaning up..."
	@rm -rf __pycache__
	@rm -rf **/__pycache__
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	@rm -rf dist
	@rm -rf build
	@rm -rf *.egg-info
	@echo "Clean complete."

fclean: clean ## cleanに加えて仮想環境も削除
	@echo "Full Cleaning up..."
	@rm -rf $(VENV)
	@echo "Full Clean complete."

re: clean all
