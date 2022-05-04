import sublime, sublime_plugin
import os
import subprocess
from threading import Thread

buildThread = None

settings = sublime.load_settings('CmakeBuild.sublime-settings')
print(settings.get('template'))


def delete(path):
    if os.path.isfile(path):
        os.remove(path)
    else:
        names = os.listdir(path)
        for name in names:
            absPath = os.path.join(path, name)
            delete(absPath)
        os.rmdir(path)
    print('remove path:', path)


def _cmakeBuildRun(path, buildName):
    global settings
    buildFolder = os.path.join(path, buildName)
    command = 'cd ' + buildFolder + ' && cmake -G "{}" .. && cmake --build .'.format(
        settings.get('template'))
    print('cmake command:', command)
    logFile = open(os.path.join(path, 'log.txt'), 'w')
    rfd, wfd = os.pipe()
    output = os.fdopen(wfd)
    proc = subprocess.Popen(command,
                            shell=True,
                            stdout=output,
                            stderr=output,
                            universal_newlines=True,
                            bufsize=1)
    os.close(wfd)
    rfile = os.fdopen(rfd, 'r')
    while True:
        line = rfile.readline()
        if not line:
            if proc.poll() is not None:
                break
            continue
        print(line, end='')
        logFile.write(line)
        logFile.flush()
    logFile.close()
    rfile.close()
    print('proc execute finished')


def build(path, clean=True):
    global buildThread
    if buildThread:
        print('join thread')
        buildThread.join()
    if not path: return
    if not os.path.isdir(path):
        print('passing path is not dir')
        return
    names = os.listdir(path)
    if not os.path.exists(os.path.join(path, 'CMakeLists.txt')):
        print('no CMakeLists.txt found')
        return
    buildName = 'build'
    buildFolder = os.path.join(path, buildName)
    if clean:
        print('clean', buildName)
        if os.path.exists(buildFolder):
            delete(buildFolder)
    if not os.path.exists(buildFolder):
        os.mkdir(buildFolder)
    buildThread = Thread(target=_cmakeBuildRun, args=(path, buildName))
    buildThread.setDaemon(True)
    buildThread.start()


class CmakeBuildCommand(sublime_plugin.TextCommand):

    def run(self, edit, paths=None):
        path = paths[0] if paths else None
        build(path)
