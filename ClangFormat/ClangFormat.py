import sublime
import sublime_plugin

import os
import json

import time
from time import sleep
import traceback

from ClangFormat.core.Worker import Worker, instance
from ClangFormat.core.FormatHandler import FormatHandler
from ClangFormat.core.Singleton import Singleton
from ClangFormat.core.Settings import Settings

import threading
from threading import Thread

_settings = {}


def _loadSettings():
    global _settings
    _settings.clear()
    settingsPath = os.path.join(sublime.packages_path(),
                                'ClangFormat/ClangFormat.sublime-settings')
    if os.path.exists(settingsPath):
        try:
            with open(settingsPath, 'r') as file:
                _settings.update(json.loads(file.read()))
        except Exception as e:
            traceback.print_exc(e)
    print(_settings)
    return _settings


class Handler(FormatHandler):

    def onStart(self, total):
        print('start format', total)
        sublime.active_window().active_view().erase_status('format_path')

    def onFormat(self, path, idx):
        print('format', idx, 'file:', path)
        sublime.active_window().active_view().set_status(
            "format_path", 'current format: ' + path)

    def onFinish(self):
        print('finish format')
        sublime.active_window().active_view().erase_status("format_path")


_loadSettings()
worker = instance(_settings, True)


@Singleton
class ClangFormatDispatcher:

    def __init__(self):
        self._initialize()

    def _initialize(self):
        global worker
        worker.setFormatHandler(Handler())

    def dispatch(self, paths):
        global worker
        for path in paths:
            if not path: continue
            if os.path.isfile(path):
                if not worker.postSavedFile(path):
                    # manager.exec(path)
                    print('{} post failed'.format(path))
            else:
                worker.addFolder(path)
                worker.workAsync()

    def cancel(self, paths):
        global worker
        for path in paths:
            if not os.path.isdir(path):
                # manager.remove(path)
                print('{} is not included'.format(path))
            else:
                print('remove folder:', path)
                worker.removeFolder(path)

    def invalidate(self):
        global worker
        worker.wait()
        worker.clean()
        print('clean worker')
        # manager.reset()


def dispatcher():
    return ClangFormatDispatcher()


class ClangFormatListener(sublime_plugin.EventListener):

    def on_post_save(self, view):
        path = view.file_name()
        settingsPath = os.path.join(
            sublime.packages_path(),
            'ClangFormat/ClangFormat.sublime-settings')
        if path and os.path.samefile(path, settingsPath):
            print('load ClangFormat sublime-settings')
            _loadSettings()
            global _settings
            Settings.setDefFormatOnSave(_settings['format_on_save'])
            print('change settings default value of format_on_save')
            return
        dispatcher().dispatch([path])
        pass

    def on_modified(self, view):
        # path = view.file_name()
        # if not path: return
        # global manager
        # formatter = manager.formatter(path)
        # if formatter:
        #     formatter.modified = True
        pass

    def on_pre_close_window(self, window):
        print('close window')

    def on_pre_close_project(self, window):
        dispatcher().cancel(window.folders())
        pass

    def on_pre_close(self, view):
        print('close view')
        if view.file_name():
            dispatcher().cancel([view.file_name()])

    def on_window_command(self, window, command, args):
        if command == 'exit':
            print('sublime exit')
            dispatcher().invalidate()


class ClangFormatCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        dispatcher().dispatch([self.view.file_name()])


class ClangFormatProjectCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        dispatcher().dispatch(sublime.active_window().folders())


class CleanFormatCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        dispatcher().invalidate()
        pass


class ClangFormatFolderCommand(sublime_plugin.TextCommand):

    def run(self, edit, paths=None):
        dispatcher().dispatch(paths)


class ClangFormatFileCommand(sublime_plugin.TextCommand):

    def run(self, edit, paths):
        dispatcher().dispatch(paths)
