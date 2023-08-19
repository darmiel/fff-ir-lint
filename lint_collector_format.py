""" Result Collector
"""

from lint import Result


class FatResult:
    """ FatResult is a data class for result values
    """

    def __init__(self, file_path: str, lnr: int, line: str, result: Result) -> None:
        self.file_path = file_path
        self.lnr = lnr
        self.line = line
        self.result = result

    def to_obj(self):
        return {
            "file": self.file_path,
            "lnr": self.lnr,
            "line": self.line,
            "result": self.result.to_obj(),
        }


class Collector:
    """ Collector collects all results for all files for later use
    """

    def __init__(self) -> None:
        self.results = {}

    def result(self, file_path: str, lnr: int, line: str, result: Result) -> None:
        """ Collect all results separated by file
        """
        if file_path not in self.results:
            self.results[file_path] = []
        self.results[file_path].append(FatResult(file_path, lnr, line, result))
