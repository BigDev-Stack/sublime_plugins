import sublime, sublime_plugin
import os

ignore = False


class DocerCommand(sublime_plugin.TextCommand):

    def run(self, edit, **kwargs):
        global ignore
        ignore = True
        current = kwargs['current']
        view = sublime.active_window().active_view()
        view.insert(edit, current, kwargs['content'])


def isDocerLine(line):
    trimmedLine = line.strip(' \n')
    return trimmedLine.startswith('/*') or (not trimmedLine.startswith('*/')
                                            and trimmedLine.startswith('*'))


def checkDocerRegion(region):
    view = sublime.active_window().active_view()
    total = view.size()
    while True:
        nextRegion = view.full_line(region.b)
        if region.b == nextRegion.b:
            return 2
        if view.substr(nextRegion).strip(' \n').startswith('*'):
            return 1
        return 2
        region = nextRegion
    raise RuntimeError('should not at here')


def handleInput(changes):
    add = 0
    hasEnter = False
    for change in changes:
        if change.str.find('\n') != -1:
            hasEnter = True
        if change.a.pt < change.b.pt:
            add -= change.len_utf8
        else:
            add += len(change.str)
    return hasEnter, add


class DocerListener(sublime_plugin.TextChangeListener):

    def on_text_changed(self, changes):
        global ignore
        if ignore:
            ignore = False
        else:
            view = sublime.active_window().active_view()
            path = view.file_name()
            if not path: return
            lastChange = changes[-1]
            hasEnter, add = handleInput(changes)
            if not hasEnter:
                # print('no enter press, ignored')
                return
            current = lastChange.a.pt if lastChange.b.pt > lastChange.a.pt else lastChange.b.pt + len(
                lastChange.str)
            region = view.full_line(current)
            line = view.substr(region)
            # print('current line:', line)
            prevRegion = view.full_line(region.a - 1)
            prevLine = view.substr(prevRegion)
            # print('prev line:', prevLine)
            if not isDocerLine(prevLine):
                # print('not docer line')
                return
            print('detect docer line')
            idx = prevLine.count(' ')
            inserted = ''
            if prevLine[idx] == '/':
                inserted += ' * \n'
                inserted += prevLine[:idx]
                inserted += ' */'
            else:
                inserted += '* '
            ret = checkDocerRegion(region)
            view.run_command('docer', {
                'ret': ret,
                'current': current,
                'content': inserted
            })
