import sublime, sublime_plugin

import os


class SuperSave(sublime_plugin.TextCommand):

    def run(self, edit):
        for view in sublime.active_window().views():
            path = view.file_name()
            if not path: continue
            if view.is_dirty() and not view.is_loading():
                view.run_command('save')
                print('save:', path)