""" Produces GitHub-Markdown friendly output for GitHub Actions
"""

from typing import List

from lint import ErrorCounter, create_error_indicator_str
from lint_collector_format import Collector, FatResult


class GitHubFormatTwo:
    """ GitHub-Markdown Format using Collector

    # File [%d warnings]
    ```diff

    ```
    > Note(Suggestion): `%s`
    """

    def __init__(self) -> None:
        self.collector = Collector()

    def file_done_callback(self, file_path: str, _: ErrorCounter) -> None:
        """ Lint callback after file has been processed
        """
        results: List[FatResult] = self.collector.results.get(file_path)
        if results is None:
            return

        print(f"## `🐛 {file_path}` [{len(results)} errors]")
        for i, result in enumerate(results):
            if i != 0:  # print separator
                print("\n---\n")

            # print diff with error
            print("```diff")
            print(f"# Line {result.lnr}:")
            print(f"- {result.line}")
            print(" ", create_error_indicator_str(len(result.line), result.result.indicators))
            print(f"@@ {result.result.error} @@")
            print("```")

            # print suggestion
            if result.result.suggestion is not None:
                print(f"> (**suggestion**): `{result.result.suggestion}`")

            print()


def result_github_2_output():
    """ Simple github callback 2
    """
    fmt = GitHubFormatTwo()
    return {
        "result": fmt.collector.result,
        "file_done": fmt.file_done_callback,
    }
