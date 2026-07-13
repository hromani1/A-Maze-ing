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

    def build(self, x: int, y: int, direction: Direction) -> None:
        """Builds the given wall in the given cell and its adjacent"""
        if not self.valid_bound(x, y, direction):
            raise ValueError("Out of bounds")
        self.grid[y][x] |= (1 << direction)
        dx, dy = direction.delta
        nx, ny = dx + x, dy + y
        self.grid[ny][nx] |= (1 << direction.opposite)

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

    def is_open_cell(self, cell: tuple[int, int]) -> bool:
        """Checks if there is an open 3x3 block starting from the given cell"""
        x, y = cell[0], cell[1]
        if x + 2 >= self.width or y + 2 >= self.height:
            return False
        for i in range(3):
            vert = self.grid[y + i][x + 1]
            if vert & (1 << Direction.EAST) | vert & (1 << Direction.WEST):
                return False
        for i in range(3):
            hori = self.grid[y + 1][x + i]
            if hori & (1 << Direction.NORTH) | hori & (1 << Direction.SOUTH):
                return False
        return True

    def is_open_block(self, cell: tuple[int, int]) -> bool:
        """Checks if the given cell is in any open 3x3 block"""
        x, y = cell[0], cell[1]
        for i in range(3):
            for j in range(3):
                if y - i >= 0 and x - j >= 0:
                    if self.is_open_cell((x - j, y - i)):
                        return True
        return False

    def get_candidates(self) -> list[tuple[tuple[int, int], Direction]]:
        """Gets the candidate walls to be carved"""
        candidates: list[tuple[tuple[int, int], Direction]] = []
        for i in range(self.height):
            for j in range(self.width):
                curr = self.grid[i][j]
                valid = self.valid_bound(j, i, Direction.EAST)
                if j + 1 < self.width and i + 1 < self.height:
                    ptrn_x = curr != 15 and self.grid[i][j + 1] != 15
                    ptrn_y = curr != 15 and self.grid[i + 1][j] != 15
                else:
                    ptrn_x = curr != 15
                    ptrn_y = curr != 15
                if valid and ptrn_x and curr & (1 << Direction.EAST):
                    candidates.append(((j, i), Direction.EAST))
                valid = self.valid_bound(j, i, Direction.SOUTH)
                if valid and ptrn_y and curr & (1 << Direction.SOUTH):
                    candidates.append(((j, i), Direction.SOUTH))
        return candidates

    def braid(self) -> None:
        """Makes the maze imperfect"""
        candidates = self.get_candidates()
        self._rng.shuffle(candidates)
        nb: int = max(1, (self.width * self.height) // 15)
        for cdd in candidates:
            if nb > 0:
                self.carve(cdd[0][0], cdd[0][1], cdd[1])
                if self.is_open_block(cdd[0]):
                    self.build(cdd[0][0], cdd[0][1], cdd[1])
                else:
                    nb -= 1
            else:
                break

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
        if not self.perfect:
            self.braid()

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
    gen = MazeGenerator(20, 15, (0, 0), (9, 7), False, 42)
    gen2 = MazeGenerator(20, 15, (0, 0), (9, 7), False, 42)
    gen3 = MazeGenerator(20, 15, (0, 0), (9, 7), True, 42)
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
    for y in range(gen.height):
        for x in range(gen.width):
            assert not gen.is_open_cell((x, y)), f"open 3x3 at ({x},{y})"
    print("No open 3x3 blocks: OK")

    # A2: pattern intact after braiding
    bitmap = ["1.1 111", "1.1 ..1", "111 111", "..1 1..", "..1 111"]
    off_x = (gen.width - 7) // 2
    off_y = (gen.height - 5) // 2
    for i, row in enumerate(bitmap):
        for j, ch in enumerate(row):
            if ch == "1":
                assert gen.grid[off_y + i][off_x + j] == 15, \
                    f"pattern cell broken at ({off_x + j},{off_y + i})"
    print("42 intact: OK")

    # A4: wall counts, perfect vs imperfect
    walls_imp = sum(bin(c).count("1") for row in gen.grid for c in row)
    walls_per = sum(bin(c).count("1") for row in gen3.grid for c in row)
    print(f"Walls perfect={walls_per}, imperfect={walls_imp}")
    assert walls_imp < walls_per
