""" Produces a simple, human-readable output
"""

from lint import create_error_indicator_array
from lint import Result

def result_simple_output():
    """ Simple format callback
    """
    def inner(_: str, lnr: int, line: str, result: Result):
        # print line number
        print("Error in line", lnr)
        print(f"'{line}'")

        mark = create_error_indicator_array(len(line), result.indicators, symbol='↑')
        print("", ''.join(mark))
        print((' '*(mark.index("↑") + 1)) + "[error]:", result.error)

        # print suggestion
        if result.suggestion is not None:
            print(f"[suggested] '{result.suggestion}'")
        print("---")
    return inner
