from ClangFormat.core.FileFormatter import FileFormatter
from ClangFormat.core.FormatUtil import isCxxFile
from ClangFormat.core.singleton import Singleton
import os


@Singleton
class OrphanedFormatManager:

    def __init__(self, settings):
        self._formatters = {}
        self._globalSettings = settings

    def _checkoutFormatter(self, filePath):
        formatter = self._formatters.get(filePath, None)
        if not formatter:
            formatter = FileFormatter(filePath)
            self._formatters[filePath] = formatter
        return formatter

    def exec(self, filePath):
        if not os.path.isfile(filePath) or not isCxxFile(filePath):
            return
        formatter = self._checkoutFormatter(filePath)
        autoFormat = self._globalSettings['format_on_save']
        if formatter and autoFormat:
            formatter.format(self._globalSettings['executable'])

    def formatter(self, path):
        return self._formatters.get(path)

    def reset(self):
        self._formatters.clear()

    def remove(self, path):
        if self._formatters.get(path):
            print('remove formatter at', path)
            del self._formatters[path]