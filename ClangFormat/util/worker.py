import os
from ClangFormat.util.format_handler import FormatHandler

from ClangFormat.util.settings import Settings, SETTINGS_NAME
from ClangFormat.util.format_util import formatFile, isCxxFile, isExcluded
from ClangFormat.util.singleton import Singleton
from ClangFormat.util.file_tree import FileTree

from threading import Thread


@Singleton
class Worker(object):

    def __init__(self, folders):
        self._folders = [folder for folder in folders]
        self._formatHandler = None
        self._thread = None
        self._tree = FileTree('')

    def setFormatHandler(self, handler):
        self._formatHandler = handler

    def _scan(self, curPath, parentTree):
        curName = os.path.basename(curPath)
        tree = parentTree.child(curName)
        if tree and tree.attach:
            print(curPath, 'has scanned')
            return
        tree = parentTree.checkout(curName)
        names = os.listdir(curPath)
        try:
            settingsIdx = names.index(SETTINGS_NAME)
        except:
            settingsIdx = -1
        parentAttach = parentTree.attach
        settings = Settings(
            parentAttach[1] if parentAttach else None,
            None if settingsIdx == -1 else os.path.join(
                curPath, names[settingsIdx]))
        if settingsIdx != -1:
            names.pop(settingsIdx)
        found = parentAttach[0] if parentAttach else False
        subNames = []
        ignored = settings['ignored']
        for name in names:
            absPath = os.path.join(curPath, name)
            if os.path.isdir(absPath):
                if not isExcluded(absPath, ignored):
                    subNames.append(name)
            elif not found and name == '.clang-format':
                found = True
            elif isCxxFile(absPath) and not isExcluded(absPath, ignored):
                tree.paths.add(absPath)
        tree.attach = (found, settings)
        for name in subNames:
            self._scan(os.path.join(curPath, name), tree)

    def _debug(self):
        children = self._tree.children()
        while children:
            tree = children.pop(0)
            if tree.paths:
                print(tree.paths)
            for sub in tree.children():
                children.append(sub)

    def _ifFolderIgnored(self, folder):
        if not self._tree.hasChild(): return False
        tree = self._tree
        parts = folder.split(os.sep)
        while parts:
            part = parts[0]
            sub = tree.child(part)
            if not sub: break
            tree = sub
            parts.pop(0)
        if not parts: tree = tree.parent
        if not tree.attach: return False
        settings = tree.attach[1]
        return isExcluded(folder, settings['ignored'])

    def _scanFolder(self, folder):
        if self._ifFolderIgnored(folder):
            print('folder is ignored')
            return
        parent = os.path.dirname(folder)
        if parent == folder:
            tree = self._tree
        else:
            tree = self._tree.build(parent)
        self._scan(folder, tree)

    def _update(self):
        while self._folders:
            folder = self._folders.pop(0)
            if not os.path.exists(folder) or not os.path.isdir(folder):
                continue
            self._scanFolder(folder)

    def __repr__(self):
        pass

    def _workOnFiles(self, found, paths):
        for idx, path in enumerate(paths):
            if self._formatHandler:
                self._formatHandler.onFormat(path, idx + 1)
            formatFile(path, found)
        paths.clear()

    def _workOnTree(self, tree):
        if tree.attach:
            self._workOnFiles(tree.attach[0], tree.paths)
        for sub in tree.children():
            self._workOnTree(sub)

    def _refershTreeChildren(self, tree, prefix):
        settings = tree.attach[1]
        ignored = settings['ignored']
        removed = []
        names = os.listdir(prefix)
        for child in tree.children():
            try:
                names.pop(names.index(child.name))
            except:
                pass
            path = os.path.join(prefix, child.name)
            if isExcluded(path, ignored):
                removed.append(child.name)
        for name in removed:
            tree.removeChild(name)
            print('remove child:', os.path.join(prefix, name))
        for child in tree.children():
            self._refershTreeChildren(child, os.path.join(prefix, child.name))
        for name in names:
            absPath = os.path.join(prefix, name)
            if not os.path.isdir(absPath) or isExcluded(absPath, ignored):
                continue
            print('new child:', absPath)
            self._scan(absPath, tree)

    def _reload(self, path):
        folder = os.path.dirname(path)
        subTree = self._tree.getTree(folder)
        if subTree:
            print('reload format settings')
            settings = subTree.attach[1]
            settings.loadFrom(path)
            self._refershTreeChildren(subTree, subTree.prefix())
            return True
        return False

    def _workRun(self):
        self._update()
        formatCount = self._tree.fileCount()
        if not formatCount:
            print('no file need format')
            return
        if self._formatHandler:
            self._formatHandler.onStart(formatCount)
        for tree in self._tree.children():
            self._workOnTree(tree)
        if self._formatHandler:
            self._formatHandler.onFinish()

    def workAsync(self):
        self.wait()
        self._thread = Thread(target=self._workRun)
        self._thread.start()

    def work(self):
        self.wait()
        self.workAsync()
        self.wait()

    def postFile(self, path):
        if not os.path.exists(path):
            return False
        if os.path.basename(path) == SETTINGS_NAME:
            return self._reload(path)
        if not isCxxFile(path): return False
        tree = self._tree.getTree(os.path.dirname(path))
        if not tree:
            return False
        settings = tree.attach[1]
        if isExcluded(path, settings['ignored']):
            return False
        if settings['format_on_save']:
            formatFile(path, tree.attach[0])
        else:
            tree.paths.add(path)
        return True

    def postSavedFile(self, path):
        return self.postFile(path)

    @property
    def path(self):
        return self._folder

    def addFolder(self, folder):
        tree = self._tree.getTree(folder)
        if tree and tree.attach:
            print('folder has processed')
            return
        self._folders.append(folder)

    def removeFolder(self, folder):
        if os.path.isdir(folder):
            tree = self._tree.getTree(folder)
            if not tree:
                return
            tree.parent.removeChild(tree.name)

    def wait(self):
        if self._thread:
            self._thread.join()
            self._thread = None

    def clean(self):
        self._tree.removeChildren()


def instance():
    return Worker([])
