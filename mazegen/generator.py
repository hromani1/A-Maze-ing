from enum import IntEnum
import random


class Direction(IntEnum):
    """Class containing the directions and their properties"""
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    @property
    def delta(self) -> tuple[int, int]:
        """The coordinates of the next cell based on direction"""
        return {
            Direction.NORTH: (0, -1),
            Direction.EAST: (1, 0),
            Direction.SOUTH: (0, 1),
            Direction.WEST: (-1, 0),
        }[self]

    @property
    def opposite(self) -> "Direction":
        """The opposite of a given direction"""
        return {
            Direction.NORTH: Direction.SOUTH,
            Direction.EAST: Direction.WEST,
            Direction.SOUTH: Direction.NORTH,
            Direction.WEST: Direction.EAST,
        }[self]


class MazeGenerator():
    """The class containing the functions and variables for maze generation"""
    def __init__(self, width: int, height: int, entry: tuple[int, int],
                 exit_: tuple[int, int], perfect: bool,
                 seed: int | None) -> None:
        """Initializes the class"""
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_ = exit_
        self.perfect = perfect
        self._rng = random.Random(seed)
        self.grid: list[list[int]] = [[15] * width for _ in range(height)]

    def valid_bound(self, x: int, y: int, direction: Direction) -> bool:
        """Checks if the given cell is inbound for the carve function"""
        dx, dy = direction.delta
        nx, ny = dx + x, dy + y
        return (nx in range(0, self.width)) and (ny in range(0, self.height))

    def carve(self, x: int, y: int, direction: Direction) -> None:
        """Carves the given wall from the given cell and its adjacent"""
        if not self.valid_bound(x, y, direction):
            return
        self.grid[y][x] &= ~(1 << direction)
        dx, dy = direction.delta
        nx, ny = dx + x, dy + y
        self.grid[ny][nx] &= ~(1 << direction.opposite)
