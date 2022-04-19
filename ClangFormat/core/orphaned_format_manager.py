import sublime
from ClangFormat.core.file_formatter import FileFormatter
from ClangFormat.core.format_util import isCxxFile
from ClangFormat.core.singleton import Singleton
import os


@Singleton
class OrphanedFormatManager:

    def __init__(self):
        self._formatters = {}

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
        autoFormat = sublime.load_settings('ClangFormat.sublime-settings').get(
            'format_on_save', False)
        if formatter and autoFormat:
            formatter.format()

    def formatter(self, path):
        return self._formatters.get(path)

    def reset(self):
        self._formatters.clear()

    def remove(self, path):
        if self._formatters.get(path):
            print('remove formatter at', path)
            del self._formatters[path]