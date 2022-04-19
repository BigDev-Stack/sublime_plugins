import sublime, sublime_plugin
import os
import subprocess


class CmakeBuildCommand(sublime_plugin.TextCommand):

    def run(self, edit, paths=None):
        path = paths[0] if paths else None
        if not path: return
        if not os.path.isdir(path):
            print('passing path is not dir')
            return
        names = os.listdir(path)
        if not os.path.exists(os.path.join(path, 'CMakeLists.txt')):
            print('no CMakeLists.txt found')
            return
        buildFolder = os.path.join(path, 'build')
        if not os.path.exists(buildFolder):
            os.mkdir(buildFolder)
        command = 'cd ' + buildFolder + ' && cmake .. && cmake --build .'
        p = subprocess.Popen(command,
                             shell=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             universal_newlines=True)
        out, err = p.communicate()
        msg = out if out else err
        if msg:
            print(msg)
            self.view.set_status("cmake_build_msg",
                                 "cmake build message: " + msg)
            with open(os.path.join(path, 'log.txt'), 'w') as f:
                f.write(msg)
