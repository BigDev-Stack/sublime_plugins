import os


def formatFile(filePath, found):
    command = 'clang-format -style='
    command += 'file' if found == True else 'Google'
    filePath = '\"' + filePath + '\"'
    command += ' ' + filePath + ' -i ' + filePath
    print('exec command:', command)
    os.popen(command)


def findUpward(path, fileName, recursive=True):
    dirPath = os.path.dirname(path)
    while path != dirPath:
        names = os.listdir(dirPath)
        for name in names:
            if name == fileName:
                return True
        if not recursive:
            break
        path = dirPath
        dirPath = os.path.dirname(path)
    return False


cxxFormats = ['h', 'hxx', 'hu', 'hpp', 'c', 'cpp', 'cxx', 'cc', 'cu']


def isCxxFile(path):
    global cxxFormats
    if not path:
        return False
    idx = path.rfind('.')
    if idx == -1:
        return False
    fmt = path[idx + 1:]
    for cxxFmt in cxxFormats:
        if cxxFmt == fmt:
            return True
    return False


def isExcluded(path, excludes):
    if not excludes: return False
    for exclude in excludes:
        idx = path.find(exclude)
        if idx == -1:
            continue
        end = idx + len(exclude)
        if end >= len(path):
            return True
        ch = path[end]
        if ch == os.sep:
            return True
    return False
