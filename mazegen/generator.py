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
        return (nx in range(0, self.width)
                ) and (ny in range(0, self.height))

    def carve(self, x: int, y: int, direction: Direction) -> None:
        """Carves the given wall from the given cell and its adjacent"""
        if not self.valid_bound(x, y, direction):
            raise ValueError("Out of bounds")
        self.grid[y][x] &= ~(1 << direction)
        dx, dy = direction.delta
        nx, ny = dx + x, dy + y
        self.grid[ny][nx] &= ~(1 << direction.opposite)

    def push(self, cell: tuple[int, int],
             stack: list[tuple[int, int]], visited: list[list[bool]]) -> None:
        """Pushes a cell into the stack and marks it visited"""
        stack.append(cell)
        visited[cell[1]][cell[0]] = True

    def get_neighbors(self, cell: tuple[int, int], visited:
                      list[list[bool]]) -> list[tuple[int, int, Direction]]:
        """"Gets the unvisited neighbors of a cell"""
        unvisited: list[tuple[int, int, Direction]] = []
        for direction in Direction:
            dx, dy = direction.delta
            nx, ny = cell[0] + dx, cell[1] + dy
            if self.valid_bound(cell[0], cell[1],
                                direction) and not visited[ny][nx]:
                unvisited.append((nx, ny, direction))
        return unvisited

    def generate(self) -> None:
        """Generates a maze from the grid"""
        visited: list[list[bool]] = [[False] * self.width
                                     for _ in range(self.height)]
        stack: list[tuple[int, int]] = []
        self.push(self.entry, stack, visited)
        while stack:
            neighbors = self.get_neighbors(stack[-1], visited)
            if neighbors:
                chosen_cell = self._rng.choice(neighbors)
                self.carve(stack[-1][0], stack[-1][1], chosen_cell[2])
                self.push((chosen_cell[0], chosen_cell[1]), stack, visited)
            else:
                stack.pop()


if __name__ == "__main__":
    gen = MazeGenerator(10, 10, (0, 0), (3, 2), True, 42)
    gen2 = MazeGenerator(10, 10, (0, 0), (3, 2), True, 42)
    gen.generate()
    print("1st maze")
    hex_grid = [[f"{num:X}" for num in sublist] for sublist in gen.grid]
    print(*hex_grid, sep="\n")
    print("2nd maze")
    gen2.generate()
    hex_grid2 = [[f"{num:X}" for num in sublist] for sublist in gen2.grid]
    print(*hex_grid2, sep="\n")

