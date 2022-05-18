from ClangFormat.core.FormatUtil import formatFile, findUpward
import os
import sublime


class FileFormatter:

    def __init__(self, filePath):
        self._path = filePath
        self._found = findUpward(filePath, '.clang-format')
        self._modified = True

    def format(self, executable):
        if self._modified:
            self._modified = not formatFile(self._path, self._found,
                                            executable)

    @property
    def modified(self):
        return self._modified

    @modified.setter
    def modified(self, flag):
        self._modified = flag