"""Output writer for maze generator.

Writes a maze grid, entry/exit coordinates, and solution path
to a file in the subject's specified format.
"""

import os


class OutputError(Exception):
    """Raised when writing the output file fails."""


def write_output(
    output_path: str,
    grid: list[list[int]],
    entry: tuple[int, int],
    exit_: tuple[int, int],
    path: list[str],
) -> None:
    """Write maze data to the output file.

    Args:
        output_path: Destination file path.
        grid: 2D list of wall bitmasks.
        entry: (x, y) entry coordinates.
        exit_: (x, y) exit coordinates.
        path: List of direction letters (N, E, S, W).
    Raises:
        OutputError: If the directory does not exist or writing fails.
    """
    directory = os.path.dirname(output_path)
    if directory and not os.path.isdir(directory):
        raise OutputError(
            f"Output directory does not exist: {directory!r}"
        )

    try:
        with open(output_path, "w", encoding="utf-8") as fh:
            for row in grid:
                line = "".join(f"{cell:X}" for cell in row)
                fh.write(line + "\n")
            fh.write("\n")
            fh.write(f"{entry[0]},{entry[1]}\n")
            fh.write(f"{exit_[0]},{exit_[1]}\n")
            fh.write(f"{''.join(path)}\n")
    except OSError as exc:
        msg = f"Cannot write output file {output_path!r}: {exc}"
        raise OutputError(msg) from exc
