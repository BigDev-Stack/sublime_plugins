import sublime, sublime_plugin
import os


def parseClassName(clazz):
    if not clazz:
        return False
    ch = clazz[0]
    if not ((ch >= 'a' and ch <= 'z') or
            (ch >= 'A' and ch <= 'Z') or ch == '_'):
        return False
    if ch == '_' and len(clazz) == 1:
        return False
    for ch in clazz[1:]:
        if not ((ch >= 'a' and ch <= 'z') or
                (ch >= 'A' and ch <= 'Z') or ch == '_' or
                (ch >= '0' and ch <= '9')):
            return False
    return True


def createCxxTemplate(path, isCpp):
    if not os.path.exists(path) or os.path.isfile(path):
        print('invalid path:', path)
        return

    def on_done(usrInput):
        print('user input:', usrInput)
        print('create cxx files at', path)
        usrInput = usrInput.strip(' ')
        if not parseClassName(usrInput):
            print('invalid class name')
            return
        fileName = usrInput
        print('file name:', fileName)
        prefix = os.path.join(path, fileName)
        headerPath = prefix + '.h'
        srcPath = prefix + ('.cc' if isCpp else '.c')
        if not os.path.exists(headerPath):
            with open(headerPath, 'w') as file:
                file.write('#pragma once\n\n')
                if isCpp:
                    file.write('class {} {};'.format(usrInput, '{}'))
        if not os.path.exists(srcPath):
            with open(srcPath, 'w') as file:
                file.write('#include "{}"\n'.format(fileName + '.h'))

    def on_cancel():
        print('cancel')

    window = sublime.active_window()
    window.show_input_panel("cxx name", "", on_done, None, on_cancel)


class CxxCommand(sublime_plugin.TextCommand):

    def run(self, edit, paths=None):
        if not paths:
            print('no path specified')
            return
        createCxxTemplate(paths[0], True)


class CCommand(sublime_plugin.TextCommand):

    def run(self, edit, paths=None):
        if not paths:
            print('no path specified')
            return
        createCxxTemplate(paths[0], False)
