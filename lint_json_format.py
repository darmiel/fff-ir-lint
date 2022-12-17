""" Produces JSON friendly output for GitHub Actions
"""

import json
from typing import List

from lint import ErrorCounter
from lint_collector_format import Collector, FatResult

class JsonFormat:
    def __init__(self) -> None:
        self.collector = Collector()
        self.files = {}

    def file_done_callback(self, file_path: str, _: ErrorCounter) -> None:
        """ Lint callback after file has been processed
        """
        results: List[FatResult] = self.collector.results.get(file_path)
        if results is None:
            return
        if not file_path in self.files:
            self.files[file_path] = []
        obj = [z.to_obj() for z in results]
        for res in obj:
            res.pop("file")
        self.files[file_path].extend(obj)
    
    def all_done_callback(self, _: ErrorCounter) -> None:
        print(json.dumps(self.files, indent=4))

def result_json_output():
    fmt = JsonFormat()
    return {
        "result": fmt.collector.result,
        "file_done": fmt.file_done_callback,
        "all_done": fmt.all_done_callback,
    }