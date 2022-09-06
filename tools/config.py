import os
import sys

if os.path.exists("config.json"): # is it config.json?
    import json # import json
    try: # try
        with open("config.json", "r+", encoding="utf-8") as f: # read a config.json with encode utf-8 
            config = json.load(f) # config is config.json's content
    except Exception as E: # is Error
        print(f"Error: {E}") # error content print
#
# elif os.path.exists("config.yaml"):
#    import yaml
#
#    try:
#        with open("config.yaml", "r+", encoding='utf-8') as f:
#            config = yaml.load(f)
#    except Exception as E:
#        print(f"Error: {E}")
#
# elif os.path.exists("config.toml"):
#    import tomli
#
#    try:
#        with open("config.toml", "rb", encoding='utf-8') as f:
#            config = tomli.load(f)
#    except Exception as E:
#        print(f"Error: {E}")
else: # is not config.json
    print("Error: No config file found") # config.json is not found
    sys.exit(-1) # no run

config = config # config(global) is config
