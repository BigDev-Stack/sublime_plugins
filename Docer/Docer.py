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
    return trimmedLine.startswith('/*') or (trimmedLine[0] == '*'
                                            and trimmedLine[1] != '/')


def checkDocerRegion(region):
    view = sublime.active_window().active_view()
    currentRegion = region
    while True:
        if currentRegion.a == 0:
            return False
        prevRegion = view.full_line(currentRegion.a - 1)
        prevLine = view.substr(prevRegion)
        trimmedLine = prevLine.strip(' \n')
        if trimmedLine.startswith('/*') or trimmedLine.endswith('/*'):
            return True
        if trimmedLine.startswith('*/') or trimmedLine.endswith('*/'):
            return False
        currentRegion = prevRegion


def hasDocerEnd(region):
    view = sublime.active_window().active_view()
    total = view.size()
    while True:
        nextRegion = view.full_line(region.b)
        if nextRegion.b == region.b:
            return False
        nextLine = view.substr(nextRegion)
        trimmedLine = nextLine.strip(' \n')
        if trimmedLine.startswith('*/') or trimmedLine.endswith('*/'):
            return True
        if trimmedLine.startswith('/*') or trimmedLine.endswith('/*'):
            return False
        region = nextRegion


def handleInput(changes):
    add = 0
    hasEnter = False
    string = ''
    for change in changes:
        if change.str.find('\n') != -1:
            hasEnter = True
        if change.a.pt < change.b.pt:
            add -= change.len_utf8
            if add >= 0:
                string = string[:add]
        else:
            add += len(change.str)
            string += change.str
    return hasEnter, add, string


class DocerListener(sublime_plugin.TextChangeListener):

    def on_text_changed(self, changes):
        global ignore
        if ignore:
            ignore = False
        else:
            view = sublime.active_window().active_view()
            path = view.file_name()
            if not path: return
            fmtIdx = path.rfind('.')
            if fmtIdx == -1:
                print('unknown file format')
                return
            fmt = path[fmtIdx:]
            for cxxFmt in [
                    '.h', '.hxx', '.hu', '.hpp', '.c', '.cc', '.cpp', '.cu'
            ]:
                if fmt == cxxFmt:
                    break
            else:
                return
            lastChange = changes[-1]
            hasEnter, add, string = handleInput(changes)
            if not hasEnter:
                return
            current = lastChange.a.pt if lastChange.b.pt > lastChange.a.pt else lastChange.b.pt + len(
                lastChange.str)
            region = view.full_line(current)
            line = view.substr(region)
            if not checkDocerRegion(region):
                return
            mode = 1 if hasDocerEnd(region) else 2
            prevRegion = view.full_line(region.a - 1)
            prevLine = view.substr(prevRegion)
            print('detect docer line:', mode, add)
            enterIdx = string.find('\n')
            filled = len(string) - enterIdx - 1
            print('filled:', filled)
            inserted = ''
            total = prevLine.rfind('*')
            print(total - filled, total, filled)
            for i in range(0, total - filled):
                inserted += ' '
            inserted += '* '
            if mode == 2:
                inserted += '\n'
                for i in range(0, total):
                    inserted += ' '
                inserted += '*/'
            view.run_command('docer', {
                'current': current,
                'content': inserted
            })
