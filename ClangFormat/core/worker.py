import os
from ClangFormat.core.FormatHandler import FormatHandler

from ClangFormat.core.Settings import Settings, SETTINGS_NAME
from ClangFormat.core.FormatUtil import formatFile, isCxxFile, isExcluded
from ClangFormat.core.Singleton import Singleton
from ClangFormat.core.FileTree import FileTree

from threading import Thread


@Singleton
class Worker(object):

    def __init__(self, folders, settings, bootstrap):
        self._folders = [folder for folder in folders]
        self._formatHandler = None
        self._thread = None
        self._tree = FileTree('')
        self._globalSettings = settings
        Settings.setDefFormatOnSave(settings['format_on_save'])
        if bootstrap:
            self._update()

    def setFormatHandler(self, handler):
        self._formatHandler = handler

    def _recursiveScan(self, path, parentTree):
        baseName = os.path.basename(path)
        # tree = parentTree.child(baseName)
        # if tree and tree.attach:
        #     print('path', path, 'has scanned')
        #     return
        tree = parentTree.checkout(baseName)
        settingsPath = os.path.join(path, SETTINGS_NAME)
        hasSetting = os.path.exists(settingsPath)
        found = os.path.exists(os.path.join(path, '.clang-format'))
        if not parentTree.attach:
            settings = Settings(None, settingsPath if hasSetting else None)
        else:
            settings = Settings(parentTree.attach,
                                settingsPath if hasSetting else None)
        if found:
            settings['has_config'] = True
        names = os.listdir(path)
        if hasSetting:
            names.remove(SETTINGS_NAME)
        if found:
            names.remove('.clang-format')
        subFolderNames = []
        ignored = settings['ignored']
        for name in names:
            absPath = os.path.join(path, name)
            if isExcluded(absPath, ignored):
                if tree.hasSubDir(name):
                    # name is excluded now, refresh
                    tree.removeChild(name)
                    print('remove path:', absPath)
                continue
            if os.path.isdir(absPath):
                # if not tree.hasSubDir(name):
                subFolderNames.append(name)
            elif isCxxFile(absPath):
                tree.newPath(absPath)
        tree.attach = settings
        for name in subFolderNames:
            self._recursiveScan(os.path.join(path, name), tree)

    def _debug(self):
        children = self._tree.children()
        while children:
            tree = children.pop(0)
            if tree.paths:
                print(tree.paths)
            for sub in tree.children():
                children.append(sub)

    def _ifFolderIgnored(self, folder):
        tree, match = self._tree.match(folder)
        ignored = None
        if not match:
            # tree exists but no attach
            # so tree's path is not scanned
            if not tree.attach:
                return False
            ignored = tree.attach['ignored']
        else:
            # path is not included
            # so check parent path
            if not tree.parent or not tree.parent.attach:
                return False
            ignored = tree.parent.attach['ignored']
        return isExcluded(folder, ignored)

    def _scanFolder(self, folder):
        if self._ifFolderIgnored(folder):
            # print('folder is ignored')
            return
        tree = self._tree.getTree(folder)
        refersh = tree and not tree.attach
        parent = os.path.dirname(folder)
        if parent == folder:
            parentTree = self._tree
        else:
            parentTree = self._tree.build(parent)
        self._recursiveScan(folder, parentTree)
        if refersh:
            print('detect parent folder:', folder)
            print('refersh folder:', folder)
            self._refershTreeChildren(tree, folder)

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
            formatFile(path, found, self._globalSettings['executable'])
        paths.clear()

    def _workOnTree(self, tree):
        if tree.attach:
            self._workOnFiles(tree.attach['has_config'], tree.modified)
        for sub in tree.children():
            self._workOnTree(sub)

    def _refershTreeChildren(self, tree, prefix):
        settings = tree.attach
        ignored = settings['ignored']
        removed = []
        names = os.listdir(prefix)
        for child in tree.children():
            names.remove(child.name)
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
            self._recursiveScan(absPath, tree)

    def _reload(self, path):
        folder = os.path.dirname(path)
        sub = self._tree.getTree(folder)
        if sub:
            print('reload format settings')
            settings = sub.attach
            if settings:
                settings.loadFrom(path)
                self._refershTreeChildren(sub, folder)
            else:
                print('folder', folder, 'has not build yet')
            return True
        return False

    def _workRun(self):
        self._update()
        formatCount = self._tree.fileCount(True)
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
        self.wait()
        if not os.path.exists(path):
            return False
        if os.path.basename(path) == SETTINGS_NAME:
            return self._reload(path)
        if not isCxxFile(path): return False
        tree = self._tree.getTree(os.path.dirname(path))
        if not tree:
            return False
        settings = tree.attach
        if not settings:
            print('path', os.path.dirname(path), 'has not build yet')
            return False
        if isExcluded(path, settings['ignored']):
            print('path {} is ignored'.format(path))
            return False
        # if settings['format_on_save']:
        #     formatFile(path, settings['has_config'],
        #                self._globalSettings['executable'])
        # else:
        #     tree.markModified(path)
        if tree.markModified(path):
            if settings['format_on_save']:
                formatFile(path, settings['has_config'],
                           self._globalSettings['executable'])
                tree.modified.clear()
        return True

    def postSavedFile(self, path):
        return self.postFile(path)

    @property
    def path(self):
        return self._folder

    def addFolder(self, folder):
        # tree = self._tree.getTree(folder)
        # if tree and tree.attach:
        #     print('folder has processed')
        #     return
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

    @property
    def tree(self):
        return self._tree


def instance(settings, bootstrap=False):
    return Worker([], settings, bootstrap)
