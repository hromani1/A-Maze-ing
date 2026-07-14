# """Manual menu test — non-interactive, all options verified
#  programmatically."""

# import os
# import sys
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# from config_parser import parse_config
# from mazegen.generator import MazeGenerator
# from display import render, CYAN, render_plain, RED,
#  YELLOW, GREEN, BLUE, MAGENTA
# from output_writer import write_output


# def test_all_options():
#     """Test menu options without user input."""

#     # Setup: create a maze
#     cfg = parse_config("config.txt")
#     gen = MazeGenerator(
#         cfg.width, cfg.height, cfg.entry, cfg.exit_,
#         cfg.perfect, cfg.seed,
#     )
#     gen.generate()
#     path = gen.solve()

#     grid = gen.grid
#     entry = cfg.entry
#     exit_ = cfg.exit_

#     print("=" * 70)
#     print("TEST 1: Default render (no path, default colors)")
#     print("=" * 70)
#     print(render(grid, entry, exit_, None))
#     print()

#     print("=" * 70)
#     print("TEST 2: With path (default colors)")
#     print("=" * 70)
#     print(render(grid, entry, exit_, path))
#     print()

#     print("=" * 70)
#     print("TEST 3: Color scheme 1 (ocean: green/blue/magenta)")
#     print("=" * 70)
#     scheme1 = {"entry": GREEN, "exit": BLUE, "path": MAGENTA}
#     print(render(grid, entry, exit_, path, scheme1))
#     print()

#     print("=" * 70)
#     print("TEST 4: Color scheme 2 (forest: yellow/red/green)")
#     print("=" * 70)
#     scheme2 = {"entry": YELLOW, "exit": RED, "path": GREEN}
#     print(render(grid, entry, exit_, path, scheme2))
#     print()

#     print("=" * 70)
#     print("TEST 5: Re-generation produces different maze")
#     print("=" * 70)
#     gen2 = MazeGenerator(
#         cfg.width, cfg.height, cfg.entry, cfg.exit_,
#         cfg.perfect, None,  # seed=None = random
#     )
#     gen2.generate()
#     path2 = gen2.solve()
#     print("First maze entry cell:", grid[entry[1]][entry[0]])
#     print("Second maze entry cell:", gen2.grid[entry[1]][entry[0]])
#     print("Different?", grid != gen2.grid)
#     print()

#     print("=" * 70)
#     print("TEST 6: render_plain strips colors")
#     print("=" * 70)
#     colored = render(grid, entry, exit_, path)
#     plain = render_plain(grid, entry, exit_, path,)
#     has_ansi = "\033[" in plain
#     print(f"Colored has ANSI: {('\033[' in colored)}")
#     print(f"Plain has ANSI: {has_ansi}")
#     print("PASS" if not has_ansi else "FAIL")
#     print()

#     print("=" * 70)
#     print("ALL TESTS COMPLETE")
#     print("=" * 70)


# if __name__ == "__main__":
#     test_all_options()
