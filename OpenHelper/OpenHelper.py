import sublime, sublime_plugin

import os
import subprocess

def genOpenDirCommand(path):
    if sublime.platform() == 'windows':
        return 'explorer "' + path + '"'
    elif sublime.platform() == 'linux':
        return 'nautilus --browser {}'.format(path)
    elif sublime.platform()=='osx':
        return 'open "{}"'.format(path)


def genOpenShellCommand(path):
    if sublime.platform() == 'windows':
        path = "'" + path + "'"
        return 'start powershell -NoExit Set-Location ' + path
    elif sublime.platform() == 'linux':
        return 'gnome-terminal --window --working-directory={}'.format(path)
    elif sublime.platform()=='osx':
        command="""osascript -e 'tell application "Terminal" to activate' -e 'tell application "Terminal" to do script "cd \\"{}\\" "'""".format(path)
        return command


class OpenPathCommand(sublime_plugin.TextCommand):

    def run(self, edit, paths=[]):
        if not paths: return
        view = sublime.active_window().active_view()
        for path in paths:
            view.erase_status("open_path")
            if os.path.isdir(path):
                command = genOpenDirCommand(path)
            else:
                view.set_status("open_path",
                                "path " + path + " is not directory")
                continue
            p = subprocess.Popen(command,
                                 shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)
            out, err = p.communicate()
            # print(err)
            # print(out, err)
            if out:
                view.set_status("open_path", "open path: " + path + ' ' + out)
            if err:
                view.set_status("open_path", "open path: " + path + ' ' + err)

        def _callback():
            view.erase_status('open_path')

        sublime.set_timeout(_callback, 3000)


class OpenTerminalCommand(sublime_plugin.TextCommand):

    def run(self, edit, paths=[]):
        if not paths: return
        view = sublime.active_window().active_view()
        for path in paths:
            view.erase_status("open_terminal")
            if not os.path.isdir(path):
                view.set_status("open_terminal", path + ' is not directory')
                continue
            command = genOpenShellCommand(path)
            view.set_status("open_terminal", command)
            print(command)
            p = subprocess.Popen(command,
                                 shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)

        def _callback():
            view.erase_status('open_terminal')

        sublime.set_timeout(_callback, 3000)
