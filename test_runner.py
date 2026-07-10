import os
from config_parser import ConfigError, parse_config

TEST_DIR = "tests"

for filename in sorted(os.listdir(TEST_DIR)):
    path = os.path.join(TEST_DIR, filename)
    try:
        result = parse_config(path)
        print(f"[OK]   {filename:30s} -> {result}")
    except ConfigError as e:
        print(f"[ERR]  {filename:30s} -> {e}")
