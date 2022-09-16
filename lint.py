""" Lint-Core:
roughly checks an .ir file for errors.
no warranty.
"""

import re

from io import TextIOWrapper
from typing import List
from difflib import get_close_matches

EXIT_NONE = 0
EXIT_CURRENT_LINE = 1
EXIT_ALL_LINES = 2
EXIT_CURRENT_CHECK_FOR_ALL_LINES = 3

###

class ErrorIndicator:
    """ Represents the start and end index of a string to be marked

    'hello w0rld!'
            ^
    [start: 7, end: 8 => '0']
    """
    def __init__(self, start: int, end: int) -> None:
        self.start = start
        self.end = end

    def fix(self, line: str) -> None:
        """ correct -1 values for start and end

        `start` and `end` = -1
        can be specified to automatically fill the length with the length of the line.
        Since the length of the string is not known to the Mark class,
        this method is used which corrects the length
        """
        if self.start == -1:
            self.start = len(line)
        if self.end == -1:
            self.end = len(line)

def create_error_indicator_array(
    length: int, indicators: List[ErrorIndicator], symbol='^'
) -> List[str]:
    """ Create ErrorIndicator character array for input of length `length`

    Returns an array which has at least the length of the parameter `length`.
    If the index of the array is contained in `marks`, the position is `symbol`, otherwise ` `.

    Attributes:
        length: Minimum length of the array
        marks: List of Marks
        symbol: Symbol to fill if index in marks
    """
    res = [' '] * length
    for indicator in indicators:
        if len(res) <= indicator.end:
            res.extend([' '] * (indicator.end - len(res)))
        for i in range(indicator.end - indicator.start):
            res[indicator.end - i - 1] = symbol
    return res

def create_error_indicator_str(length: int, indicators: List[ErrorIndicator]) -> str:
    """ Combines ErrorIndicator character array to single string

    Returns a string with the values from array joined with ''
    """
    return ''.join(create_error_indicator_array(length, indicators))

###

class Result:
    """ Result holds the lint result for a single line for a specific check

    Also controls if the current test should be cancelled
    """

    def __init__(self,
        exit_rule: int, indicators: List[ErrorIndicator], error: str, suggestion: str
    ) -> None:
        self.exit_rule = exit_rule
        self.indicators = indicators
        self.error = error
        self.suggestion = suggestion

    def update(self, line: str):
        """ Fix all ErrorIndicators from current test
        """
        for indicator in self.indicators:
            indicator.fix(line)

    def with_exit_rule(self, exit_rule: int) -> 'Result':
        """ Controls how to continue after the check

        One of the following values can be returned:
            EXIT_NONE: Do nothing special, just continue checking
            EXIT_CURRENT_LINE: Don't check current line anymore, go to next line
            EXIT_ALL_LINES: Don't check anything anymore
            EXIT_CURRENT_CHECK_FOR_ALL_LINES: Don't run current check on any other lines
        """
        self.exit_rule = exit_rule
        return self

def multi_indicator_result(
    indicators: List[ErrorIndicator], error: str, suggestion: str = None
) -> Result:
    """ Result with multiple ErrorIndicators

    'Hello 012 World 345'
           ^^^       ^^^
    """
    return Result(-1, indicators, error, suggestion)

def single_indicator_result(
    mark_from: int, mark_to: int, error: str, suggestion: str = None
) -> Result:
    """ Result with single ErrorIndicator

    'Hello 012 World'
           ^^^
    """
    return multi_indicator_result([ErrorIndicator(mark_from, mark_to)], error, suggestion)

def single_indicator_result_from(mark_from: int, error: str, suggestion: str = None) -> Result:
    """ Result with single ErrorIndicator starting from `mark_from`
    """
    return single_indicator_result(mark_from, -1, error, suggestion)

def single_indicator_result_to(mark_to: int, error: str, suggestion: str = None) -> Result:
    """ Result with single ErrorIndicator from start to `mark_to`
    """
    return single_indicator_result(0, mark_to, error, suggestion)

# aliases
mir = multi_indicator_result
sir = single_indicator_result
sirf = single_indicator_result_from
sirt = single_indicator_result_to

###

class Context:
    """ Shared context for all checks

    Can be used to check if another check already failed or to store data between checks
    """
    def __init__(self) -> None:
        self.result = {}
        self.last_key = None

    def update_result(self, check: type, result: Result) -> None:
        """ Update check `result` for specified `check`
        """
        self.result[check] = result

    def did_check_fail(self, check: type) -> bool:
        """ Returns if a `check` already failed
        """
        return check in self.result

    def set_last_key(self, key: str) -> None:
        """ Updates the last processed key from a key-value pair
        """
        self.last_key = key

###

class Check:
    """ Check represents a check for one line
    """

    def __init__(self) -> None:
        self.active = True

    def check(self, ctx: Context, lnr: int, line: str) -> Result:
        """ Check `line` against current check
        """

    def ignore_if_failed(self) -> list:
        """ Do not run this check if one of the returned checks failed
        """

    def set_active(self, active: bool):
        """ Can be used to disable a check for all other lines
        """
        self.active = active

    def is_active(self) -> bool:
        """ Returns if the current check is active
        """
        return self.active

class EmptyLineCheck(Check):
    """ Checks for empty lines
    """
    def check(self, ctx: Context, lnr: int, line: str) -> Result:
        if len(line.strip()) == 0:
            return sir(0, 1, \
                "empty lines are not allowed. use comments for separation", suggestion="#"
            ).with_exit_rule(EXIT_CURRENT_LINE)
        return None

class WhiteSpaceCommentCheck(Check):
    """ Checks for white space before comments
    '  # test'
     ^^
    """
    def check(self, ctx: Context, lnr: int, line: str) -> Result:
        if line.strip().startswith("#") and not line.startswith("#"):
            return sirt(
                line.index("#"), "white space before comment not allowed", suggestion=line.strip()
            ).with_exit_rule(EXIT_CURRENT_LINE)
        return None

class WhiteSpaceCheck(Check):
    """ Checks for whitespace at the end of a line
    'name: test '
               ^
    """
    def __init__(self) -> None:
        super().__init__()
        self.start_pattern = re.compile(r"^([\s]+)")
        self.end_pattern = re.compile(r"([\s]+)$")
        self.multi_space_pattern = re.compile(r"\s{2,}")

    def ignore_if_failed(self) -> list:
        return [WhiteSpaceCommentCheck]

    def check(self, ctx: Context, _: int, line: str) -> Result:
        # start of line
        res = self.start_pattern.findall(line)
        if len(res) > 0:
            return sirt(len(res[0]), "lines cannot start with spaces", suggestion=line.lstrip(' '))
        # end of line
        res = self.end_pattern.findall(line)
        if len(res) > 0:
            return sirf(len(line) - len(res[0]),
                "lines cannot end with spaces", suggestion=line.rstrip(' '))
        # check using 'strip'
        if line.strip() != line:
            return sirf(0, "lines cannot start or end with whitespace", suggestion=line.strip())
        # multi space check
        res = []
        for search in self.multi_space_pattern.finditer(line):
            span = search.span()
            res.append(ErrorIndicator(span[0], span[1]))
        if len(res) > 0:
            suggestion = line
            while '  ' in suggestion:
                suggestion = suggestion.replace('  ', ' ')
            return mir(res, "lines cannot contain double spaces", suggestion=suggestion)
        # all fine :)
        return None

class DescriptorCheck(Check):
    """ Checks first two lines for expected .ir header
    """
    def __init__(self) -> None:
        super().__init__()
        self.version_pattern = re.compile(r"^Version:\s\d+$")

    def check(self, ctx: Context, lnr: int, line: str) -> Result:
        if lnr == 1 and line != "Filetype: IR signals file" and line != "Filetype: IR library file":
            return sirf(0, "first line must contain 'Filetype: IR signals file'",
                suggestion='Filetype: IR signals file')
        if lnr == 2 and not self.version_pattern.match(line):
            return sirf(0, "second line must contain 'Version: \\d'",
                suggestion='Version: 1')
        return None

class NonASCIICheck(Check):
    """ Checks a line for non-ASCII characters
    """
    def __init__(self) -> None:
        super().__init__()
        self.pattern = re.compile(r"[^\x20-\x7E\xB0\x09]")

    def check(self, ctx: Context, lnr: int, line: str) -> Result:
        resp = []
        for search in self.pattern.finditer(line):
            span = search.span()
            resp.append(ErrorIndicator(span[0], span[1]))
        if len(resp) > 0:
            suggestion = ''.join(self.pattern.split(line))
            # if we remove non-ASCII chars there's probably some double spaces ['  ']
            while '  ' in suggestion:
                suggestion = suggestion.replace('  ', ' ')
            return mir(resp, "non-ASCII character/s found", suggestion=suggestion) \
                .with_exit_rule(EXIT_CURRENT_LINE)
        return None

class KeyValueValidityCheck(Check):
    """
    checks if an .ir file only contains valid key-value pairs
    'test: abc'
     ^^^^

    'test:abc'
     ^^^^^^^^
    """
    def __init__(self) -> None:
        super().__init__()
        self.pattern_str = r"^([A-Za-z-_]+):\s.+$"
        self.pattern = re.compile(self.pattern_str)
        self.valid_keys = [
            "Filetype", "Version", # header
            "name", "type", "protocol", "address", "command", # parsed signal
            "frequency", "duty_cycle", "data" # raw signal
        ]

    def ignore_if_failed(self) -> list:
        """
        do not check if line 1 or 2 are not vaild
        """
        return [DescriptorCheck]

    def check(self, ctx: Context, lnr: int, line: str) -> Result:
        # parse key
        if not ':' in line:
            return sirf(0, "line is no key-value pair. 'key: value' expected") \
                .with_exit_rule(EXIT_CURRENT_LINE)

        # check that value starts witih ' '
        # 'name:value' should be 'name: value'
        value_start_index = line.index(":") + 1
        if not line[value_start_index:].startswith(' '):
            # error but don't stop processing current line
            return sir(
                value_start_index - 1, value_start_index, "space missing after ':'",
                suggestion=line[:value_start_index] +" " + line[value_start_index:]
            )

        # check generic pattern
        if not self.pattern.match(line):
            return sirf(0, f"key-value pattern does not match expression '{self.pattern_str}'")

        # check if key is valid
        key = line[:line.index(":")]
        if not key in self.valid_keys:
            # find best similar key
            similar = get_close_matches(key, self.valid_keys)
            suggestion = None
            if len(similar) > 0:
                suggestion = f"{similar[0]}:{line[value_start_index:]}"
            return sirt(len(key), f"key '{key}' unknown", suggestion=suggestion) \
                .with_exit_rule(EXIT_NONE)
        ctx.set_last_key(key)
        return None

class SignalKeyOrderCheck(Check):
    """ Check order of key-value pairs

    since the order of the key-value pairs is important, the order is checked here.
    `name` must always be followed by `type`, `protocol` by `address` and so on.
    otherwise there will be problems
    """
    def __init__(self) -> None:
        super().__init__()
        self.ignored_order_keys = [
            "Filetype", "Version"
        ]
        self.value_space_pattern = re.compile(r"^[\s]{3,}")
        self.expected_key = None
        self.order = {
            "name": "type",
            "type": {
                "parsed": "protocol",
                "raw": "frequency"
            },

            "protocol": "address",
            "address": "command",
            "command": "name",

            "frequency": "duty_cycle",
            "duty_cycle": "data",
            "data": ["data", "name"]
        }

    def check(self, ctx: Context, lnr: int, line: str) -> Result:
        split = line.split(":", 1)
        if len(split) != 2:
            return sirf(0, f"cannot unpack key-value {len(split)} > 2")
        key, value = split
        key, value = key.strip(), value.strip()

        if key in self.ignored_order_keys:
            return None

        key_end = line.index(":")

        value_start = key_end + 1
        for char in line[key_end + 1:]:
            if char == ' ':
                value_start += 1
            else:
                break

        if not key in self.order:
            return sirt(key_end, "key has no order-rule") \
                .with_exit_rule(EXIT_CURRENT_CHECK_FOR_ALL_LINES)

        # always start order-search with "name"
        if self.expected_key is None:
            self.expected_key = "name"

        if isinstance(self.expected_key, list):
            if not key in self.expected_key:
                return sirt(key_end, f"one of keys '{', '.join(self.expected_key)}' expected") \
                    .with_exit_rule(EXIT_CURRENT_CHECK_FOR_ALL_LINES)
        else:
            if key != self.expected_key:
                return sirt(
                    key_end, f"key '{self.expected_key}' expected",
                    suggestion=f"{self.expected_key}: ..."
                ).with_exit_rule(EXIT_CURRENT_CHECK_FOR_ALL_LINES)

        next_expected = self.order[key]
        if isinstance(next_expected, (str, list, )):
            self.expected_key = next_expected
        elif isinstance(next_expected, dict):
            if not value in next_expected:
                e_k = ', '.join(next_expected.keys())
                return sirf(value_start, f"[lint]: can't find next expected key in [{e_k}]") \
                    .with_exit_rule(EXIT_CURRENT_CHECK_FOR_ALL_LINES)
            self.expected_key = next_expected[value]
        else:
            return sirt(key_end,
                "[lint]: something weird happened. Please create an issue on GitHub.") \
                .with_exit_rule(EXIT_CURRENT_CHECK_FOR_ALL_LINES)

        return None

class DataValidityCheck(Check):
    """ Checks if the data is valid

    protocol: NECexf
              ^^^^^^ (should be NECext)

    data: 100 213 1-1 42
                   ^

    address: 10 FG FF AA
                 ^
    """
    def __init__(self) -> None:
        super().__init__()
        self.space_pattern = re.compile("\\s+")
        self.valid_protocols = [
            "RC6",
            "RC5",
            "RC5X",
            "NEC",
            "NECext",
            "NEC42",
            "NEC42ext",
            "SIRC",
            "SIRC15",
            "SIRC20",
            "Samsung32"
        ]

    def ignore_if_failed(self) -> list:
        return [KeyValueValidityCheck]

    def check_data(self, key: str, value: str) -> List[ErrorIndicator]:
        marks = []
        begin = True
        for idx, char in enumerate(value):
            if char == ' ':
                begin = True
                continue
            if char == "-" and begin:
                begin = False
                continue
            if not char.isdigit():
                indicator_index = len(key) + 1 + idx
                marks.append(ErrorIndicator(indicator_index, indicator_index + 1))
            begin = False
        return marks

    def check_hex(self, key: str, value: str) -> List[ErrorIndicator]:
        marks = []
        begin = True
        for idx, char in enumerate(value):
            if char == ' ':
                begin = True
                continue
            if char not in "0123456789ABCDEFabcdef":
                indicator_index = len(key) + 1 + idx
                marks.append(ErrorIndicator(indicator_index, indicator_index + 1))
        return marks

    def check(self, ctx: Context, lnr: int, line: str) -> Result:
        split = line.split(":", 1)
        if len(split) != 2:
            return sirf(0, "cannot unpack key-value")
        key, value = split

        value_start = line.index(value.strip(), len(key))

        if key == "data":
            marks = self.check_data(key, value)
            if len(marks) > 0:
                return mir(marks, "character not allowed here (non-Digit)")

        elif key in ("address", "command"):
            marks = self.check_hex(key, value)
            if len(marks) > 0:
                return mir(marks, "character not allowed here (non-HEX)")

        elif key == "protocol":
            if value.strip() not in self.valid_protocols:
                similar = get_close_matches(value, self.valid_protocols)
                suggestion = None
                if len(similar) > 0:
                    suggestion = f"{key}: {similar[0]}"
                return sirf(value_start, 
                    f"Protocol '{value.strip()}' unknown", suggestion=suggestion)
        
        elif key == "duty_cycle":
            try:
                float_value = float(value.strip())
                if float_value < 0 or float_value > 1:
                    return sirf(value_start, "duty_cycle must be between 0.0 and 1.0")
            except ValueError:
                return sirf(value_start, "duty_cycle must be a float")
        
        return None

###

def check_file(file_path: str, file_descriptor: TextIOWrapper, on_found = None) -> bool:
    """ Checks a file for errors
    """

    # these checks are applied to "normal" lines
    normal_checks = [
        EmptyLineCheck(),
        WhiteSpaceCommentCheck(),
        WhiteSpaceCheck(),
        DescriptorCheck(),
        KeyValueValidityCheck(),
        SignalKeyOrderCheck(),
        DataValidityCheck(),
        NonASCIICheck(),
    ]

    # these checks are applied to commented lines
    comment_checks = [
        NonASCIICheck(),
    ]

    did_pass = True
    context = Context()

    for _lnr, line in enumerate([z.strip("\n") for z in file_descriptor.readlines()]):
        lnr = _lnr + 1 # human readable line numbers

        # comments
        if line.startswith("#"):
            checks = comment_checks
        else:
            checks = normal_checks

        for check in [z for z in checks if z.is_active()]:
            # check if check is disabled because a previous check failed
            if isinstance(check.ignore_if_failed, list) and type(check) in check.ignore_if_failed:
                continue

            # execute check
            resp: Result = check.check(context, lnr, line)

            # if check passed, do nothing
            if resp is None:
                continue
            elif not isinstance(resp, Result):
                print("[lint] result of response was not Result for check", type(check))
                continue
            else:
                did_pass = False

            # add line number to result and fix markers
            resp.update(line)

            # cache check result
            context.update_result(type(check), resp)

            # pass result to callback
            on_found(file_path, lnr, line, resp)

            if resp.exit_rule == EXIT_ALL_LINES:
                # cancel all other checks for all other lines
                return did_pass
            elif resp.exit_rule == EXIT_CURRENT_LINE:
                # cancel all other checks for current line
                break
            elif resp.exit_rule == EXIT_CURRENT_CHECK_FOR_ALL_LINES:
                # cancel current check for all other lines
                check.set_active(False)
                break

    return did_pass

class ErrorCounter:
    """ ErrorCounter is used to count raised total/file/line errors
    """
    def __init__(self) -> None:
        self.total_count = 0
        self.file_count = 0

    def inc_total(self):
        """ Increment total error count
        """
        self.total_count += 1

    def inc_file(self):
        """ Increment file error count.
        Also increases total count
        """
        self.file_count += 1
        self.inc_total()

    def reset_file(self):
        """ Resets file error count
        """
        self.file_count = 0
