import json
import re
import os.path

CONFIG_FILE_NAME: str = ".irlint.json"
NAME_PATTERN_KEY: str = "name-pattern"
NAME_REWRITE_KEY: str = "name-rewrites"

###

def get_name_pattern() -> re.Pattern:
    return re.compile(__config[NAME_PATTERN_KEY])

def get_name_pattern_raw() -> str:
    return __config[NAME_PATTERN_KEY]

def get_name_rewrites() -> dict:
    vals = {}
    for k, v in __config[NAME_REWRITE_KEY].items():
        if isinstance(v, list):
            for l in v:
                vals[l] = k
        elif isinstance(v, str):
            vals[v] = k
        else:
            raise KeyError("invalid type in rewrite config")
    # make key lower-case
    vals = {k.lower(): v for k, v in vals.items()}
    return vals

###

__config = {}

def load_defaults():
    vals = {
        NAME_PATTERN_KEY: r"^[A-Z0-9][a-z0-9_\-\+\s]*$",
        NAME_REWRITE_KEY: {}
    }
    for k, v in vals.items():
        if k not in __config:
            __config[k] = v

# load config from file or save default config
loaded = False
if os.path.exists(CONFIG_FILE_NAME):
    with open(CONFIG_FILE_NAME, "r") as fd:
        __config = json.load(fd)
        loaded = True
# insert any missing data
load_defaults()
# write back to file
with open(CONFIG_FILE_NAME, "w") as fd:
    json.dump(__config, fd, indent=4)
