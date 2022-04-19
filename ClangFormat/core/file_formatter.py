from ClangFormat.core.format_util import formatFile, findUpward
import os


class FileFormatter:

    def __init__(self, filePath):
        self._path = filePath
        self._found = findUpward(filePath, '.clang-format')
        self._modified = True

    def format(self):
        if self._modified:
            formatFile(self._path, self._found)
            self._modified = False

    @property
    def modified(self):
        return self._modified

    @modified.setter
    def modified(self, flag):
        self._modified = flag