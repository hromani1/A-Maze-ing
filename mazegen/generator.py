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
    """Generates grid-based mazes with reproducible seeding,
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
    """
    def __init__(self, width: int, height: int, entry: tuple[int, int],
                 exit_: tuple[int, int], perfect: bool,
                 seed: int | None) -> None:
        """Initializes the maze parameters, seeds the random number generator,
        and populates a fully walled grid.

        Args:
            width: The width of the maze grid in columns.
            height: The height of the maze grid in rows.
            entry: A coordinate tuple (x, y) representing the start cell,
            where 0 <= x < width and 0 <= y < height.
            exit_: A coordinate tuple (x, y) representing the end cell,
            where 0 <= x < width and 0 <= y < height.
            perfect: A flag that keeps the maze perfect if True,
            or runs a loop-creating braiding routine if False.
            seed: An integer value to ensure reproducible maze layouts,
            or None for randomized layouts every run.
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_ = exit_
        self.perfect = perfect
        self._rng = random.Random(seed)
        self.grid: list[list[int]] = [[15] * width for _ in range(height)]

    def _valid_bound(self, x: int, y: int, direction: Direction) -> bool:
        """Checks if the given cell is inbound for the carve function"""
        dx, dy = direction.delta
        nx, ny = dx + x, dy + y
        return (nx in range(0, self.width)
                ) and (ny in range(0, self.height))

    def _carve(self, x: int, y: int, direction: Direction) -> None:
        """carves the given wall from the given cell and its adjacent"""
        if not self._valid_bound(x, y, direction):
            raise ValueError("Out of bounds")
        self.grid[y][x] &= ~(1 << direction)
        dx, dy = direction.delta
        nx, ny = dx + x, dy + y
        self.grid[ny][nx] &= ~(1 << direction.opposite)

    def _build(self, x: int, y: int, direction: Direction) -> None:
        """builds the given wall in the given cell and its adjacent"""
        if not self._valid_bound(x, y, direction):
            raise ValueError("Out of bounds")
        self.grid[y][x] |= (1 << direction)
        dx, dy = direction.delta
        nx, ny = dx + x, dy + y
        self.grid[ny][nx] |= (1 << direction.opposite)

    def _push_s(self, cell: tuple[int, int],
                stack: list[tuple[int, int]],
                visited: list[list[bool]]) -> None:
        """Pushes a cell into the stack and marks it visited"""
        stack.append(cell)
        visited[cell[1]][cell[0]] = True

    def _get_v_neighbors(self, cell: tuple[int, int], visited:
                         list[list[bool]]) -> list[tuple[int, int, Direction]]:
        """Gets the unvisited neighbors of a cell during maze generation"""
        unvisited: list[tuple[int, int, Direction]] = []
        for direction in Direction:
            dx, dy = direction.delta
            nx, ny = cell[0] + dx, cell[1] + dy
            if self._valid_bound(cell[0], cell[1],
                                 direction) and not visited[ny][nx]:
                unvisited.append((nx, ny, direction))
        return unvisited

    def _stamp_pattern(self, visited: list[list[bool]]) -> None:
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

    def _check_endpoints(self, visited: list[list[bool]]) -> bool:
        """Checks if entry and exit are in the logo or not"""
        en = self.entry
        ex = self.exit_
        valid_en: bool = visited[en[1]][en[0]]
        valid_ex: bool = visited[ex[1]][ex[0]]
        return valid_en or valid_ex

    def _is_open_cell(self, cell: tuple[int, int]) -> bool:
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

    def _is_open_block(self, cell: tuple[int, int]) -> bool:
        """Checks if the given cell is in any open 3x3 block"""
        x, y = cell[0], cell[1]
        for i in range(3):
            for j in range(3):
                if y - i >= 0 and x - j >= 0:
                    if self._is_open_cell((x - j, y - i)):
                        return True
        return False

    def _get_candidates(self) -> list[tuple[tuple[int, int], Direction]]:
        """Gets the candidate walls to be _carved"""
        candidates: list[tuple[tuple[int, int], Direction]] = []
        for i in range(self.height):
            for j in range(self.width):
                curr = self.grid[i][j]
                valid = self._valid_bound(j, i, Direction.EAST)
                if j + 1 < self.width and i + 1 < self.height:
                    ptrn_x = curr != 15 and self.grid[i][j + 1] != 15
                    ptrn_y = curr != 15 and self.grid[i + 1][j] != 15
                else:
                    ptrn_x = curr != 15
                    ptrn_y = curr != 15
                if valid and ptrn_x and curr & (1 << Direction.EAST):
                    candidates.append(((j, i), Direction.EAST))
                valid = self._valid_bound(j, i, Direction.SOUTH)
                if valid and ptrn_y and curr & (1 << Direction.SOUTH):
                    candidates.append(((j, i), Direction.SOUTH))
        return candidates

    def _braid(self) -> None:
        """Makes the maze imperfect"""
        candidates = self._get_candidates()
        self._rng.shuffle(candidates)
        nb: int = max(1, (self.width * self.height) // 15)
        for cdd in candidates:
            if nb > 0:
                self._carve(cdd[0][0], cdd[0][1], cdd[1])
                if self._is_open_block(cdd[0]):
                    self._build(cdd[0][0], cdd[0][1], cdd[1])
                else:
                    nb -= 1
            else:
                break

    def generate(self) -> None:
        """Generates a maze from the grid"""
        visited: list[list[bool]] = [[False] * self.width
                                     for _ in range(self.height)]
        stack: list[tuple[int, int]] = []
        self._stamp_pattern(visited)
        if self._check_endpoints(visited):
            raise MazeError("Entry and exit can't be inside pattern")
        self._push_s(self.entry, stack, visited)
        while stack:
            neighbors = self._get_v_neighbors(stack[-1], visited)
            if neighbors:
                chosen_cell = self._rng.choice(neighbors)
                self._carve(stack[-1][0], stack[-1][1], chosen_cell[2])
                self._push_s((chosen_cell[0], chosen_cell[1]), stack, visited)
            else:
                stack.pop()
        if not self.perfect:
            self._braid()

    def _get_o_neighbors(self, cell: tuple[int, int], visited:
                         list[list[bool]]) -> list[tuple[int, int, Direction]]:
        """Gets the available neighbors of a cell during solving"""
        unvisited: list[tuple[int, int, Direction]] = []
        for direction in Direction:
            dx, dy = direction.delta
            nx, ny = cell[0] + dx, cell[1] + dy
            wall: bool = bool(self.grid[cell[1]][cell[0]] & (1 << direction))
            vbound: bool = self._valid_bound(cell[0], cell[1], direction)
            if vbound and not wall and not visited[ny][nx]:
                unvisited.append((nx, ny, direction))
        return unvisited

    def _push_q(self, cell: tuple[int, int],
                myque: deque[tuple[int, int]],
                visited: list[list[bool]]) -> None:
        """Pushes a cell into the dequeue and marks it visited"""
        myque.append(cell)
        visited[cell[1]][cell[0]] = True

    def _path(self, cell: tuple[int, int],
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
        self._push_q(self.entry, myque, visited)
        while myque:
            if myque[0] == self.exit_:
                return self._path(myque[0], parent)
            neighbors = self._get_o_neighbors(myque[0], visited)
            for i in range(len(neighbors)):
                chosen = neighbors[i]
                parent[(chosen[0], chosen[1])] = ((myque[0][0],
                                                  myque[0][1]), chosen[2])
                self._push_q((chosen[0], chosen[1]), myque, visited)
            myque.popleft()
        raise MazeError("No solution found! Check if the maze is generated.")
