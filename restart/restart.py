import sublime
import sublime_plugin
import sys
import subprocess
import os


class RestartCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        version = int(sublime.version()[:1])
        if version not in [2, 3, 4]:
            print('unsupported version of sublime')
            return
        if sys.platform == 'win32':
            subprocess.call('taskkill /im sublime_text.exe /f && cmd /C "' +
                            os.path.join(os.getcwd(), 'sublime_text.exe') +
                            '"',
                            shell=True)
            pass
        else:
            subprocess.call("pkill 'sublime_text' && " +
                            os.path.join(os.getcwd(), 'sublime_text'),
                            shell=True)
