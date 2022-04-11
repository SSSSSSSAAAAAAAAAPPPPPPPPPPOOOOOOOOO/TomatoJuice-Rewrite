import os
import sys

if os.path.exists("config.json"):
    import json

    try:
        with open("config.json", "r+", encoding='utf-8') as f:
            config = json.load(f)
    except Exception as E:
        print(f"Error: {E}")

elif os.path.exists("config.yaml"):
    import yaml

    try:
        with open("config.yaml", "r+", encoding='utf-8') as f:
            config = yaml.load(f)
    except Exception as E:
        print(f"Error: {E}")

elif os.path.exists("config.toml"):
    import tomli

    try:
        with open("config.toml", "rb", encoding='utf-8') as f:
            config = tomli.load(f)
    except Exception as E:
        print(f"Error: {E}")
else:
    print("Error: No config file found")
    sys.exit(-1)

config = config
