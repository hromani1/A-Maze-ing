"""Parses and validates maze configuration files."""

from dataclasses import dataclass


class ConfigError(Exception):
    """Raised when the configuration file is invalid."""


@dataclass
class Config:
    """Stores a validated maze configuration."""

    width: int
    height: int
    entry: tuple[int, int]
    exit_: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None


_VALID_KEYS: set[str] = {
    "WIDTH", "HEIGHT", "ENTRY", "EXIT",
    "OUTPUT_FILE", "PERFECT", "SEED",
}


_MANDATORY_KEYS: set[str] = {
    "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT",
}


def _parse_int(raw: str, field_name: str) -> int:
    """Convert a raw string to an int, raising ConfigError on failure."""
    try:
        return int(raw)
    except ValueError as exc:
        msg = f"{field_name} must be an integer, got: {raw!r}"
        raise ConfigError(msg) from exc


def _parse_bool(raw: str, field_name: str) -> bool:
    """Convert a raw string to a bool."""
    if raw == "True":
        return True
    if raw == "False":
        return False
    msg = (
        f"{field_name} must be exactly 'True' or 'False' (case-sensitive), "
        f"got: {raw!r}"
    )
    raise ConfigError(msg)


def _parse_coord(raw: str, field_name: str) -> tuple[int, int]:
    """Parse 'x,y' into (x, y), raising ConfigError on any problem."""
    parts = raw.split(",")
    if len(parts) != 2:
        msg = (
            f"{field_name} must be two comma-separated integers, "
            f"got: {raw!r}"
        )
        raise ConfigError(msg)
    try:
        x = int(parts[0])
        y = int(parts[1])
    except ValueError as exc:
        msg = (f"{field_name} must be two comma-separated integers, "
               f"got: {raw!r}")
        raise ConfigError(msg) from exc
    return x, y


def parse_config(path: str) -> Config:
    """Parse and validate a maze configuration file."""
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()
    except FileNotFoundError as exc:
        msg = f"Config file not found: {path!r}"
        raise ConfigError(msg) from exc
    except PermissionError as exc:
        msg = f"Permission denied reading config file: {path!r}"
        raise ConfigError(msg) from exc
    except IsADirectoryError as exc:
        msg = f"Config path is a directory, not a file: {path!r}"
        raise ConfigError(msg) from exc
    except OSError as exc:
        msg = f"Cannot read config file {path!r}: {exc}"
        raise ConfigError(msg) from exc
    raw_values: dict[str, str] = {}
    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        if "=" not in stripped:
            msg = f"Line {line_no}: missing '=' in: {stripped!r}"
            raise ConfigError(msg)
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            msg = f"Line {line_no}: empty key before '=' in: {stripped!r}"
            raise ConfigError(msg)

        if not value:
            msg = f"Line {line_no}: empty value for key {key!r}"
            raise ConfigError(msg)
        if key not in _VALID_KEYS:
            msg = f"Line {line_no}: unknown key {key!r}"
            raise ConfigError(msg)
        if key in raw_values:
            msg = f"Line {line_no}: duplicate key {key!r}"
            raise ConfigError(msg)
        raw_values[key] = value
    if not raw_values:
        msg = f"Config file {path!r} contains no valid key-value pairs"
        raise ConfigError(msg)
    missing = _MANDATORY_KEYS - raw_values.keys()
    if missing:
        msg = f"Missing mandatory key(s): {', '.join(sorted(missing))}"
        raise ConfigError(msg)
    width = _parse_int(raw_values["WIDTH"], "WIDTH")
    height = _parse_int(raw_values["HEIGHT"], "HEIGHT")
    entry = _parse_coord(raw_values["ENTRY"], "ENTRY")
    exit_ = _parse_coord(raw_values["EXIT"], "EXIT")
    output_file = raw_values["OUTPUT_FILE"]
    perfect = _parse_bool(raw_values["PERFECT"], "PERFECT")
    seed: int | None = None

    if "SEED" in raw_values:
        seed = _parse_int(raw_values["SEED"], "SEED")

    if width < 2:
        msg = f"WIDTH must be at least 2, got: {width}"
        raise ConfigError(msg)

    if height < 2:
        msg = f"HEIGHT must be at least 2, got: {height}"
        raise ConfigError(msg)

    ex, ey = entry
    if not (0 <= ex < width and 0 <= ey < height):
        msg = (
            f"ENTRY {entry} is outside the maze bounds: "
            f"({width}x{height})"
        )
        raise ConfigError(msg)

    ox, oy = exit_
    if not (0 <= ox < width and 0 <= oy < height):
        msg = (
            f"EXIT {exit_} is outside the maze bounds: "
            f"({width}x{height})"
        )
        raise ConfigError(msg)

    if entry == exit_:
        msg = f"ENTRY and EXIT cannot be the same cell: {entry}"
        raise ConfigError(msg)
    return Config(
        width=width,
        height=height,
        entry=entry,
        exit_=exit_,
        output_file=output_file,
        perfect=perfect,
        seed=seed,
    )
