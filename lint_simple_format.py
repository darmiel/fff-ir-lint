""" Produces a simple, human-readable output
"""

from lint import create_error_indicator_array
from lint import Result, ErrorCounter


def result_simple_output():
    """ Simple format callback
    """

    def result(_: str, lnr: int, line: str, result: Result) -> None:
        # print line number
        print("Error in line", lnr)
        print(f"'{line}'")

        mark = create_error_indicator_array(len(line), result.indicators, symbol='↑')
        print("", ''.join(mark))
        print((' ' * (mark.index("↑") + 1)) + "[error]:", result.error)

        # print suggestion
        if result.suggestion is not None:
            print(f"[suggested] '{result.suggestion}'")
        print("---")

    def header(file_path: str, index: int, file_count: int) -> None:
        head = f"[lint] checking '{file_path}' [{index + 1}/{file_count}]"
        print('*' * len(head))
        print(head)

    def summary(_: int, error_counter: ErrorCounter) -> None:
        print(f"[lint] found {error_counter.file_count} warnings/errors in file.")
        print()

    return {
        "result": result,
        "file_start": header,
        "file_done": summary,
    }
