*This project has been created as part of the 42 curriculum by <aalkhati>, <hromani>.*

# A-Maze-ing

## Description

A-Maze-ing is a Python maze generator that reads a plain-text configuration file, builds a random maze with an iterative recursive-backtracker, solves it with BFS, and writes the result to a file in hexadecimal wall-encoding format. It also provides an interactive terminal display with ASCII rendering, color rotation, and an optional shortest-path overlay.

### Features

- **Iterative recursive-backtracker generation** — uses an explicit Python `list` as a stack to carve passages. Produces a *perfect* maze (exactly one path between any two cells) when `PERFECT=True`.
- **BFS solver** — uses a `collections.deque` queue to guarantee the shortest path from entry to exit; works on both perfect and imperfect mazes.
- **"42" pattern** — a bitmap logo stamped in the center of the maze by pre-marking cells as visited before generation begins. If the maze is too small (`width < 9` or `height < 7`), the program prints `Too small for '42' logo` and skips the stamp. Entry and exit cannot fall inside the pattern.
- **PERFECT / imperfect mode** — when `PERFECT=False`, the generator *braids* the maze by carving additional passages while enforcing the subject's 3×3 open-area prohibition.
- **Seed-based reproducibility** — an optional `SEED` key makes every generation deterministic.
- **Interactive terminal menu** — regenerate mazes, toggle the shortest-path overlay, rotate ANSI color schemes, or quit.
- **ASCII renderer with ANSI colors** — entry marked `E`, exit marked `X`, path marked `*`. A plain-text mode (`render_plain`) strips ANSI escapes for piping to files.
- **Output validation** — the wall-coherence validator provided with the subject (`output_validator.py`) is included in the repository for convenience; our output file passes it.

## Instructions

### Prerequisites

Python 3.10 or newer must be installed. The project uses no external runtime libraries.

### Makefile targets

```bash
make install      # pip install -r requirements.txt
make run          # python3 a_maze_ing.py config.txt
make debug        # python3 -m pdb a_maze_ing.py config.txt
make lint         # flake8 . + mypy (project flags)
make lint-strict  # flake8 . + mypy --strict
make clean        # remove __pycache__, .mypy_cache, *.pyc
```

### Usage

```bash
python3 a_maze_ing.py <config_file>
```

Example:

```bash
python3 a_maze_ing.py config.txt
```

All errors (invalid configuration, impossible maze parameters, write failures) print a single clear message to stderr and exit with status 1. The program never shows a raw traceback.

### Interactive menu

After the maze is generated and written, the terminal presents four options:

1. **Re-generate a new maze** — generates a new maze and overwrites the output file. If a `SEED` was provided, each regeneration uses seed+1 (fully reproducible sequence); without `SEED`, each regeneration is freshly random.
2. **Show/Hide path from entry to exit** — toggles the shortest-path overlay (`*`) on the ASCII display.
3. **Rotate maze colors** — cycles through three predefined ANSI color schemes (walls, entry, exit, and path colors all change).
4. **Quit** — exits the program.

## Configuration file format

The configuration file contains one `KEY=VALUE` pair per line. Lines starting with `#` are comments and are ignored. Empty lines are also ignored.

| Key | Type | Example | Description |
|---|---|---|---|
| `WIDTH` | int | `WIDTH=20` | Maze width in cells (must be ≥ 2) |
| `HEIGHT` | int | `HEIGHT=15` | Maze height in cells (must be ≥ 2) |
| `ENTRY` | coord | `ENTRY=0,0` | Entry coordinates as `x,y` |
| `EXIT` | coord | `EXIT=19,14` | Exit coordinates as `x,y` |
| `OUTPUT_FILE` | string | `OUTPUT_FILE=maze.txt` | Destination file path |
| `PERFECT` | bool | `PERFECT=True` | `True` = perfect maze; `False` = braided/imperfect |
| `SEED` | int | `SEED=42` | (Optional) Random seed for reproducibility |

### Parser policies

The parser enforces three deliberate strictness rules:

1. **Case-sensitive booleans** — `PERFECT` must be exactly `True` or `False`. Variants such as `true`, `TRUE`, or `1` are rejected with `ConfigError`.
2. **Duplicate keys rejected** — If a key appears more than once, the parser raises `ConfigError` and stops.
3. **Unknown keys rejected** — Any key not listed in the table above raises `ConfigError` and stops.

These rules catch typos early and prevent silent misconfiguration.

## Maze generation algorithm & why

### Generation — iterative recursive-backtracker

The maze is generated with an iterative recursive-backtracker using an explicit Python `list` as a stack (`generator.py`, `generate()`). The algorithm starts at the entry cell, pushes it onto the stack, and repeatedly carves passages to unvisited neighbors until it reaches a dead end, then backtracks by popping the stack.

We chose this algorithm for three reasons:

1. **Perfect by construction** — As a spanning-tree algorithm, it guarantees exactly one path between any two cells when braiding is disabled.
2. **Simple to reason about** — The stack-based state makes the algorithm easy to debug and extend (e.g., stamping the "42" pattern by pre-marking cells as visited).
3. **No recursion limit** — Python's default recursion limit (~1000 frames) would cap maze size for a true recursive implementation. The explicit stack removes that ceiling.

### Solving — BFS

The solver uses Breadth-First Search with a `collections.deque` queue (`generator.py`, `solve()`).

We chose BFS for two reasons:

1. **Shortest-path guarantee** — BFS always finds the shortest path in an unweighted grid, which the subject requires for the output file.
2. **Works on imperfect mazes** — Unlike wall-following or DFS, BFS does not rely on the perfect-maze property; it correctly navigates braided mazes with multiple paths.

## Reusable module
Generates grid-based mazes with reproducible seeding,
an embedded '42' wall logo, and optional dead-end braiding.

Example:
    gen = MazeGenerator(20, 15, (0, 0), (19, 14), perfect=False, seed=42)
    gen.generate()
    gen.solve()
Attributes:
    grid: A 2D list of integers representing the wall bitmasks,
    where bit 0 = NORTH, 1 = EAST, 2 = SOUTH, and 3 = WEST.
    A set bit (1) means the wall is closed,
    while a cleared bit (0) means it is carved open.
    width: The total number of columns in the maze grid.
    height: The total number of rows in the maze grid.
    entry: The starting coordinate tuple (x, y) for the maze path.
    exit_: The ending coordinate tuple (x, y) for the maze path.
    perfect: A boolean that dictates whether the maze remains a
    perfect tree (True) or becomes braided (False).

Raises / behavior notes:
    generate() raises a MazeError if either the entry or
    exit coordinate overlaps with the coordinates of the stamped '42' logo.
    If the maze dimensions are too small (width < 9 or height < 7),
    the '42' logo stamping is skipped and a message is printed.

The generation engine is packaged as `mazegen` and can be built as a standalone Python package (`mazegen-<version>.tar.gz` or `.whl`). The `MazeGenerator` class exposes the grid structure and supports custom dimensions, entry/exit points, perfect/imperfect flags, and seeds.

Build commands:

```bash
python3 -m pip install build
python3 -m build
```

## Resources

### Python documentation

- <https://docs.python.org/3/library/dataclasses.html> — used for the `Config` data class (`config_parser.py`).
- <https://docs.python.org/3/library/enum.html> — used for the `Direction` enum (`generator.py`).
- <https://docs.python.org/3/library/collections.html#collections.deque> — used for the BFS solver queue (`generator.py`).
- Python Packaging Tutorial — <https://packaging.python.org> — followed for building the `mazegen` distributable package.

## Team & project management

### Roles

- **Hasan — Engine**: grid representation, iterative backtracker generator, BFS solver, "42" pattern stamping, braiding logic, 3×3 open-block prevention, Python packaging (`mazegen`).
- **Alaa — Shell**: configuration parser (`config_parser.py`), output writer (`output_writer.py`), ASCII display renderer (`display.py`), interactive menu (`a_maze_ing.py`), Makefile, README.

### Workflow

- **Branch-per-person** — Each team member worked on a dedicated feature branch.
- **One-file-one-owner** — Files were owned by one person to avoid merge conflicts.
- **`make lint` as merge gate** — Branches were only merged into `main` after passing flake8 and mypy with the project's mandatory flags.

### Planning & evolution

Our initial two-week plan split the work into engine (week 1) and shell (week 2). In practice, the H4 merge bottleneck delayed integration: the engine and shell branches diverged enough that the final merge required coordinated fixes, notably the CRLF line-ending saga across WSL and VS Code.

### What worked well

- Splitting the project into engine vs. shell let us work in parallel without blocking each other.
- `make lint` caught type and style issues before they reached `main`.

### What could be improved

- **Earlier integration testing** — Waiting until H4 to merge meant we discovered interface mismatches late. A mid-week "dry merge" or shared interface stub would have reduced the bottleneck.
- **Line-ending policy** — We lost time to CRLF issues between WSL and Windows. A `.gitattributes` file with `* text=auto eol=lf` should have been committed on day one.

### Tools

- **git & GitHub** — version control, branch-per-person workflow
- **VS Code + WSL** — development environment
- **flake8 & mypy** — linting and static type checking
- **make** — task automation
