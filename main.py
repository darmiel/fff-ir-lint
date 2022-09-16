""" $ python3 main.py github file_1.ir file_2.ir file_3.ir ... file_n.ir
"""

import sys

from lint import check_file
from lint import ErrorCounter, Result

from lint_simple_format import result_simple_output
from lint_github_format import result_github_output
from lint_github_2_format import result_github_2_output

FORMATS = {
    "simple": result_simple_output,
    "github": result_github_output,
    "github2": result_github_2_output,
}

def unused(*args):
    """ Dummy callback
    """
    _ = args

def main():
    """ Main entrypoint
    """

    # print syntax
    if len(sys.argv) == 0:
        print("$ python3 main.py <format> [file_1] [file_2] ... [file_n]")
        print(f"Formats: {', '.join(FORMATS.keys())}")
        return

    if sys.argv[1] not in FORMATS:
        print(f"error: Unknown format! Formats: {', '.join(FORMATS.keys())}")
        return

    fmt = FORMATS[sys.argv[1]]()
    error_callback = fmt.get("result") or unused
    file_start_callback = fmt.get("file_start") or unused
    file_done_callback = fmt.get("file_done") or unused
    all_done_callback = fmt.get("all_done") or unused

    error_counter = ErrorCounter()

    files = sys.argv[2:]
    if len(files) <= 0:
        print("[lint] no files to check")
        return

    for index, file in enumerate(files):
        error_counter.reset_file()

        file_start_callback(file, index, len(files))

        # proxy callback to count warnings
        # then pass callback to "real" error_callback
        def proxy_callback(file_path: str, lnr: int, line: str, result: Result):
            error_counter.inc_file()
            error_callback(file_path, lnr, line, result)

        with open(file, "r", encoding='UTF-8') as file_descriptor:
            check_file(file, file_descriptor, proxy_callback)
        
        file_done_callback(file, error_counter)

    all_done_callback(error_counter)

    print(f"\n[lint] found a total of {error_counter.total_count} warnings/errors")

    if error_counter.total_count != 0:
        sys.exit('[lint] found warnings/errors')

if __name__ == "__main__":
    main()
