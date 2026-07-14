import sys
import os

from config_parser import ConfigError, parse_config
from mazegen.generator import MazeError, MazeGenerator
from output_writer import OutputError, write_output
from display import render, CYAN, RED, YELLOW, GREEN, BLUE, MAGENTA, WHITE


def _pause() -> None:
    """Wait for Enter, handling EOF and interrupt gracefully."""
    try:
        input("Press Enter to continue...")
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
        raise SystemExit(0)


def _run_menu(
    gen: MazeGenerator,
    grid: list[list[int]],
    entry: tuple[int, int],
    exit_: tuple[int, int],
    path: list[str],
    output_file: str,
    seed: int | None,
) -> None:
    """Interactive terminal menu loop."""
    show_path = False
    color_index = 0
    regen_seed = seed

    color_schemes = [
        {
            "entry": CYAN, "exit": RED, "path": YELLOW, "wall": WHITE,
        },
        {
            "entry": GREEN, "exit": BLUE, "path": MAGENTA,
            "wall": CYAN,
        },
        {
            "entry": YELLOW, "exit": RED, "path": GREEN,
            "wall": YELLOW,
        },
    ]

    while True:
        os.system("clear" if os.name != "nt" else "cls")

        print("\n=== A-Maze-ing ===")
        print("1. Re-generate a new maze")
        print("2. Show/Hide path from entry to exit")
        print("3. Rotate maze colors")
        print("4. Quit")
        print()

        current_path = path if show_path else None
        colors = color_schemes[color_index]
        print(render(grid, entry, exit_, current_path, colors))
        print()

        try:
            choice = input("Choice? (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if choice == "1":
            if regen_seed is not None:
                regen_seed += 1
            gen = MazeGenerator(
                width=gen.width,
                height=gen.height,
                entry=entry,
                exit_=exit_,
                perfect=gen.perfect,
                seed=regen_seed,
            )
            gen.generate()
            path = gen.solve()
            grid = gen.grid
            write_output(output_file, grid, entry, exit_, path)
            print("Maze re-generated.")
            _pause()

        elif choice == "2":
            show_path = not show_path

        elif choice == "3":
            color_index = (color_index + 1) % len(color_schemes)

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please enter 1-4.")
            _pause()


def main() -> int:
    """Run the maze pipeline."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>", file=sys.stderr)
        return 1

    try:
        cfg = parse_config(sys.argv[1])
        gen = MazeGenerator(
            cfg.width,
            cfg.height,
            cfg.entry,
            cfg.exit_,
            cfg.perfect,
            cfg.seed,
        )
        gen.generate()
        path = gen.solve()
        write_output(
            cfg.output_file,
            gen.grid,
            cfg.entry,
            cfg.exit_,
            path,
        )
        print(f"Maze written to {cfg.output_file}")

        _run_menu(
            gen, gen.grid, cfg.entry, cfg.exit_, path,
            cfg.output_file, cfg.seed,
        )
        return 0

    except (ConfigError, MazeError, OutputError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
