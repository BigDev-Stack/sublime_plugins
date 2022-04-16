import sublime
import sublime_plugin

import os
import json

import time
from time import sleep
import traceback

from ClangFormat.util.worker import Worker, instance
from ClangFormat.util.orphaned_format_manager import OrphanedFormatManager
from ClangFormat.util.format_handler import FormatHandler
from ClangFormat.util.singleton import Singleton

import threading
from threading import Thread


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


@Singleton
class ClangFormatDispatcher:

    def __init__(self):
        self._initialize()

    def _initialize(self):
        self._manager = OrphanedFormatManager()
        self._worker = instance()
        self._worker.setFormatHandler(Handler())

    def dispatch(self, paths):
        for path in paths:
            if not path: continue
            if os.path.isfile(path):
                if not self._worker.postSavedFile(path):
                    self._manager.exec(path)
            else:
                self._worker.addFolder(path)
                self._worker.workAsync()

    def cancel(self, paths):
        for path in paths:
            if not os.path.isdir(path):
                self._manager.remove(path)
            else:
                print('remove folder:', path)
                self._worker.removeFolder(path)

    def invalidate(self):
        self._worker.wait()
        self._worker.clean()
        print('clean worker')
        self._manager.reset()


def dispatcher():
    return ClangFormatDispatcher()


class ClangFormatListener(sublime_plugin.EventListener):

    def on_post_save(self, view):
        dispatcher().dispatch([view.file_name()])
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


class ClangFormatWindowCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        dispatcher().dispatch(sublime.active_window().folders())


class CloseWindowFormatCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        dispatcher().invalidate()
        pass


class ClangFormatFolderCommand(sublime_plugin.TextCommand):

    def run(self, edit, paths=None):
        dispatcher().dispatch(paths)


class ClangFormatFileCommand(sublime_plugin.TextCommand):

    def run(self, edit, paths):
        dispatcher().dispatch(paths)
