"""Test script for A3 display.py."""

from mazegen.generator import MazeGenerator
from display import render, render_plain


def main() -> None:
    gen = MazeGenerator(
        width=20,
        height=15,
        entry=(0, 0),
        exit_=(19, 14),
        perfect=True,
        seed=42,
    )
    gen.generate()  # modifies gen.grid in place, returns None
    path = gen.solve()  # no arguments, uses self.entry/self.exit_

    print(f"Path length: {len(path)}")
    print()

    # Without path
    print("=" * 70)
    print("WITHOUT PATH (plain)")
    print("=" * 70)
    print(render_plain(gen.grid, gen.entry, gen.exit_))
    print()

    # With path
    print("=" * 70)
    print("WITH PATH (colored)")
    print("=" * 70)
    print(render(gen.grid, gen.entry, gen.exit_, path))


if __name__ == "__main__":
    main()
