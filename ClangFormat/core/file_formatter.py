from ClangFormat.core.format_util import formatFile, findUpward
import os

class FileFormatter:

    def __init__(self, filePath):
        self._path = filePath
        self._found = findUpward(filePath, '.clang-format')
        self._lastTime = -1

    def format(self):
        required = False
        if self._lastTime == -1:
            required = True
            self._lastTime = os.path.getmtime(self._path)
        else:
            time = os.path.getmtime(self._path)
            if time != self._lastTime:
                self._lastTime = time
                required = True
        if required:
            formatFile(self._path, self._found)