"""Maze ASCII renderer.

Renders a maze grid as Unicode/ASCII art with optional path overlay,
entry/exit markers, and ANSI color support.

Assumes a coherent grid with sealed borders (North+West canonical form).
Border walls are drawn unconditionally; the renderer trusts the generator
never produces open borders.
"""
import re


RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
BOLD = "\033[1m"
_ANSI_ESCAPE = re.compile(r"\033\[[0-9;]*m")


def render(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit_: tuple[int, int],
    path: list[str] | None = None,
) -> str:
    """Render a maze grid as ASCII art.

    Wall encoding (bitflags per cell):
        bit 0 (value 1)  -> North wall present
        bit 1 (value 2)  -> East  wall present
        bit 2 (value 4)  -> South wall present
        bit 3 (value 8)  -> West  wall present

    Each cell contributes:
        - a top string:  "+--" if North closed, "+  " if open
        - a side string: "|  " if West closed,  "   " if open

    Each maze row = one line of tops + closing '+',
                    one line of sides + closing '|'.
    After the last row, one bottom border line.

    Markers:
        'E' in entry cell interior (cyan)
        'X' in exit cell interior  (red)
        '*' in path cells          (yellow)

    Args:
        grid: 2-D list of wall bitmasks, grid[y][x].
        entry: (x, y) coordinates of the entry cell.
        exit_: (x, y) coordinates of the exit cell.
        path: Optional list of directions ('N','S','E','W') from entry.

    Returns:
        Multi-line string representing the rendered maze.
    """
    if not grid or not grid[0]:
        return ""
    height = len(grid)
    width = len(grid[0])

    path_cells: set[tuple[int, int]] = set()
    if path is not None:
        cx, cy = entry
        path_cells.add((cx, cy))
        deltas = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
        for direction in path:
            dx, dy = deltas[direction]
            cx += dx
            cy += dy
            path_cells.add((cx, cy))
    lines: list[str] = []

    for y in range(height):
        # Build TOP line for this row
        top = ""
        for x in range(width):
            top += "+"
            if grid[y][x] & 1:
                top += "--"
            else:
                top += "  "
        top += "+"
        lines.append(top)
        side = ""
        for x in range(width):
            if grid[y][x] & 8:
                side += "|"
            else:
                side += " "
            # Interior marker
            if (x, y) == entry:
                side += f"{CYAN}E {RESET}"
            elif (x, y) == exit_:
                side += f"{RED}X {RESET}"
            elif path is not None and (x, y) in path_cells:
                side += f"{YELLOW}* {RESET}"
            else:
                side += "  "
        side += "|"
        lines.append(side)
    bottom = ""
    for _ in range(width):
        bottom += "+--"
    bottom += "+"
    lines.append(bottom)

    return "\n".join(lines)


def render_plain(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit_: tuple[int, int],
    path: list[str] | None = None,
) -> str:
    """Same as render() but without ANSI colour codes."""
    colored = render(grid, entry, exit_, path)
    return _ANSI_ESCAPE.sub("", colored)
