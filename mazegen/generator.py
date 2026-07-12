from enum import IntEnum
import random
from collections import deque


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


class MazeError(Exception):
    """Maze Errors"""
    def __init__(self, message: str = "Unknown maze error") -> None:
        super().__init__(message)


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

    def push_s(self, cell: tuple[int, int],
               stack: list[tuple[int, int]],
               visited: list[list[bool]]) -> None:
        """Pushes a cell into the stack and marks it visited"""
        stack.append(cell)
        visited[cell[1]][cell[0]] = True

    def get_v_neighbors(self, cell: tuple[int, int], visited:
                        list[list[bool]]) -> list[tuple[int, int, Direction]]:
        """Gets the unvisited neighbors of a cell during maze generation"""
        unvisited: list[tuple[int, int, Direction]] = []
        for direction in Direction:
            dx, dy = direction.delta
            nx, ny = cell[0] + dx, cell[1] + dy
            if self.valid_bound(cell[0], cell[1],
                                direction) and not visited[ny][nx]:
                unvisited.append((nx, ny, direction))
        return unvisited

    def stamp_pattern(self, visited: list[list[bool]]) -> None:
        """This function marks the 42 logo visited"""
        has_42 = (self.width >= 9 and self.height >= 7)
        if not has_42:
            print("Too small for '42' logo")
            return
        bitmap = ["1.1 111", "1.1 ..1", "111 111", "..1 1..", "..1 111"]
        offset_x = (self.width - 7) // 2
        offset_y = (self.height - 5) // 2
        for i, row in enumerate(bitmap):
            for j, column in enumerate(row):
                if bitmap[i][j] == "1":
                    visited[offset_y + i][offset_x + j] = True

    def check_endpoints(self, visited: list[list[bool]]) -> bool:
        """Checks if entry and exit are in the logo or not"""
        en = self.entry
        ex = self.exit_
        valid_en: bool = visited[en[1]][en[0]]
        valid_ex: bool = visited[ex[1]][ex[0]]
        return valid_en or valid_ex

    def generate(self) -> None:
        """Generates a maze from the grid"""
        visited: list[list[bool]] = [[False] * self.width
                                     for _ in range(self.height)]
        stack: list[tuple[int, int]] = []
        self.stamp_pattern(visited)
        if self.check_endpoints(visited):
            raise MazeError("Entry and exit can't be inside pattern")
        self.push_s(self.entry, stack, visited)
        while stack:
            neighbors = self.get_v_neighbors(stack[-1], visited)
            if neighbors:
                chosen_cell = self._rng.choice(neighbors)
                self.carve(stack[-1][0], stack[-1][1], chosen_cell[2])
                self.push_s((chosen_cell[0], chosen_cell[1]), stack, visited)
            else:
                stack.pop()

    def get_o_neighbors(self, cell: tuple[int, int], visited:
                        list[list[bool]]) -> list[tuple[int, int, Direction]]:
        """Gets the available neighbors of a cell during solving"""
        unvisited: list[tuple[int, int, Direction]] = []
        for direction in Direction:
            dx, dy = direction.delta
            nx, ny = cell[0] + dx, cell[1] + dy
            wall: bool = bool(self.grid[cell[1]][cell[0]] & (1 << direction))
            vbound: bool = self.valid_bound(cell[0], cell[1], direction)
            if vbound and not wall and not visited[ny][nx]:
                unvisited.append((nx, ny, direction))
        return unvisited

    def push_q(self, cell: tuple[int, int],
               myque: deque[tuple[int, int]],
               visited: list[list[bool]]) -> None:
        """Pushes a cell into the dequeue and marks it visited"""
        myque.append(cell)
        visited[cell[1]][cell[0]] = True

    def path(self, cell: tuple[int, int],
             parent: dict[tuple[int, int],
                          tuple[tuple[int, int], Direction]]) -> list[str]:
        """Finds the path taken from entry to exit"""
        rev_path: list[str] = []
        current: tuple[int, int] = cell
        direction: Direction
        while current != self.entry:
            direction = parent[current][1]
            rev_path.append(direction.name[0])
            current = (parent[current][0][0], parent[current][0][1])
        return list(reversed(rev_path))

    def solve(self) -> list[str]:
        """Finds the shortest solution of the maze"""
        visited: list[list[bool]] = [[False] * self.width
                                     for _ in range(self.height)]
        myque: deque[tuple[int, int]] = deque()
        parent: dict[tuple[int, int], tuple[tuple[int, int], Direction]] = {}
        self.push_q(self.entry, myque, visited)
        while myque:
            if myque[0] == self.exit_:
                return self.path(myque[0], parent)
            neighbors = self.get_o_neighbors(myque[0], visited)
            for i in range(len(neighbors)):
                chosen = neighbors[i]
                parent[(chosen[0], chosen[1])] = ((myque[0][0],
                                                  myque[0][1]), chosen[2])
                self.push_q((chosen[0], chosen[1]), myque, visited)
            myque.popleft()
        raise MazeError("No solution found! Check if the maze is generated.")


if __name__ == "__main__":
    gen = MazeGenerator(20, 15, (0, 0), (9, 7), True, 42)
    gen3 = MazeGenerator(10, 7, (0, 0), (1, 1), True, 42)
    gen2 = MazeGenerator(5, 5, (0, 0), (4, 3), True, 42)
    gen.generate()
    print("1st maze")
    hex_grid = [[f"{num:X}" for num in sublist] for sublist in gen.grid]
    print(*hex_grid, sep="\n")
    print(gen.solve())
    print("2nd maze")
    gen2.generate()
    hex_grid2 = [[f"{num:X}" for num in sublist] for sublist in gen2.grid]
    print(*hex_grid2, sep="\n")
    print(gen2.solve())
    print("3rd maze")
    try:
        gen3.generate()
        hex_grid3 = [[f"{num:X}" for num in sublist] for sublist in gen3.grid]
        print(*hex_grid3, sep="\n")
        print(gen3.solve())
    except MazeError as e:
        print(e)
