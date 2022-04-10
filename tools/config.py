import json
import os
import sys

import tomli
import yaml

if os.path.exists("config.json"):
    try:
        with open("config.json", "r+") as f:
            config = json.load(f)
    except Exception as E:
        print(f"Error: {E}")

elif os.path.exists("config.yaml"):
    try:
        with open("config.yaml", "r+") as f:
            config = yaml.load(f)
    except Exception as E:
        print(f"Error: {E}")

elif os.path.exists("config.toml"):
    try:
        with open("config.toml", "rb") as f:
            config = tomli.load(f)
    except Exception as E:
        print(f"Error: {E}")
else:
    print("Error: No config file found")
    sys.exit(-1)

config = config
