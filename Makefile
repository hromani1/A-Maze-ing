# A-Maze-ing Makefile
# Recipe lines MUST start with a real TAB character.

.PHONY: install run debug lint lint-strict clean

PYTHON := python3

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) a_maze_ing.py config.txt

debug:
	$(PYTHON) -m pdb a_maze_ing.py config.txt

lint:
	flake8 .
	mypy . --ignore-missing-imports --warn-unused-ignores --check-untyped-defs --warn-return-any --disallow-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict --ignore-missing-imports

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
	rm -rf */.mypy_cache
	rm -rf .mypy_cache
	rm -f *.pyc maze.txt validator_out.txt