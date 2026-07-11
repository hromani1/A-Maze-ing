import sys

from config_parser import ConfigError, parse_config
from mazegen.generator import MazeError, MazeGenerator
from output_writer import OutputError, write_output


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
        return 0
    except (ConfigError, MazeError, OutputError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
