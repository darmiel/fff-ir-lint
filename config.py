import fnmatch
import json
import re
from typing import Union, Optional


def str_match_pattern(haystack: str, pattern: Union[str, re.Pattern]):
    if type(pattern) == str:
        return pattern.lower() == haystack.lower()
    elif type(pattern) == re.Pattern:
        return pattern.match(haystack.lower())


def str_get_pattern(pattern: str) -> Union[str, re.Pattern]:
    if pattern.startswith("/") and pattern.endswith("/"):
        return re.compile(pattern[1:-1])
    return pattern


class NameCheckConfig:
    prefixes: dict[str, dict[str, list[Union[str, re.Pattern]]]]

    def __init__(self, prefixes):
        self.prefixes = prefixes

    def _get_name_rewrite_for_prefix(self, prefix: str, value: str) -> Optional[str]:
        for new_name, vals in self.prefixes[prefix].items():
            for val in vals:
                if str_match_pattern(value, val):
                    return new_name
        return None

    def get_name_rewrite(self, file_name: str, value: str) -> Optional[str]:
        for prefix in self.prefixes.keys():
            if fnmatch.fnmatch(file_name.lower(), prefix.lower()):
                if res := self._get_name_rewrite_for_prefix(prefix, value):
                    return res
        return None


class Config:
    def __init__(self, name_check_config: NameCheckConfig):
        self.name_check_config = name_check_config


def load_name_check_config(data: dict) -> NameCheckConfig:
    group_list = {}
    for key, val in data.get('$groups', {}).items():
        group_list[key] = tuple(str_get_pattern(z) for z in val)

    path_prefix = data.get('$path-prefix', '')
    prefix_list: dict[str, dict[str, list[Union[str, re.Pattern]]]] = {}

    for key, val in data.items():
        if key.startswith("$"):
            continue
        signal_pattern_dict: dict[str, list[Union[str, re.Pattern]]] = {}
        for signal_name, signal_patterns in val.items():
            patterns = []
            for pattern in signal_patterns:
                # group
                if pattern.startswith("$group:"):
                    group = pattern[7:].strip()
                    patterns.extend(group_list.get(group, []))
                else:
                    patterns.append(str_get_pattern(pattern))
            signal_pattern_dict[signal_name] = patterns

        for prefix_key in key.split(","):
            prefix_key = path_prefix + prefix_key
            if prefix_key not in prefix_list:
                prefix_list[prefix_key] = signal_pattern_dict
                continue
            for new_signal_name, signal_patterns in signal_pattern_dict.items():
                if new_signal_name not in prefix_list[prefix_key]:
                    prefix_list[prefix_key][new_signal_name] = signal_patterns
                    continue
                for v in signal_patterns:
                    if v not in prefix_list[prefix_key][new_signal_name]:
                        prefix_list[prefix_key][new_signal_name].append(v)
    return NameCheckConfig(prefix_list)


def load_config(file_path: str) -> Config:
    with open(file_path, "r") as fd:
        data: dict = json.load(fd)
    ncc = load_name_check_config(data.get('name-check', {}))
    return Config(ncc)


def empty_config() -> Config:
    return Config(load_name_check_config({}))
