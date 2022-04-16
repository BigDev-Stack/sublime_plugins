import traceback
import json

SETTINGS_NAME = 'clang-format-settings.json'


class Settings:

    __initialParams__ = [('ignored', []), ('format_on_save', False)]

    def __init__(self, parent, path):
        self._parent = parent
        self._values = None
        if not path:
            if parent:
                self._values = {}
        else:
            try:
                with open(path, 'r') as file:
                    self._values = json.loads(file.read())
            except Exception as e:
                traceback.print_exc(e)
                pass
        self._check()

    def _check(self):
        if not self._parent:
            if self._values is None:
                self._values = {}
            for key, value in Settings.__initialParams__:
                if self._values.get(key) is None:
                    self._values[key] = value

    def __getitem__(self, key):
        value = self._values.get(key)
        if value is None:
            settings = self
            while value is None and settings._parent:
                settings = settings._parent
                value = settings._values.get(key)
        return value

    def __setitem__(self, key, value):
        self._values[key] = value

    def __repr__(self):
        s = '{\n'
        s += '    parent: '
        s += str(self._parent)
        for key, _ in Settings.__initialParams__:
            s += ',\n'
            s += '    '
            s += str(key)
            s += ': '
            s += str(self[key])
        s += '\n}'
        return s

    @property
    def parent(self):
        return self._parent

    def loadFrom(self, path):
        try:
            with open(path, 'r') as f:
                self._values = json.loads(f.read())
        except:
            self._values = {}