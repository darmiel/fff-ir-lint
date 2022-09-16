""" Produces GitHub-Markdown friendly output for GitHub Actions
"""

from lint import create_error_indicator_str
from lint import Result

def result_github_output():
    """ Simple github callback
    """
    headers = [] # used to check if the file already has a header
    def inner(file_path: str, lnr: int, line: str, result: Result):
        if not file_path in headers:
            headers.append(file_path)
            print(f"## `🐛 {file_path}`")
        else:
            print("\n---\n") # separator
        
        print("```diff")

        # print line number
        print(f"# Line {lnr}:")
        print(f"- {line}")
        print(" ", create_error_indicator_str(len(line), result.marks))
        print(f"@@ {result.error} @@")

        print("```")
        if result.suggestion is not None:
            print(f"> **Note**(**suggested**): `{result.suggestion}`")
    return inner
