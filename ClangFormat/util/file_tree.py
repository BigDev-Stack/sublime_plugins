import os


class FileTree:

    def __init__(self, name):
        self._paths = set()
        self._name = name
        self._children = {}
        self._par = None
        self._attach = None

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._par

    def root(self):
        tree = self
        while tree._par:
            tree = tree._par
        return tree

    def getTree(self, path):
        return self.getTree2(path.split(os.sep))

    def getTree2(self, parts):
        tree = self
        for part in parts:
            if not part: continue
            child = tree._children.get(part)
            if not child:
                return None
            tree = child
        return tree

    def hasSubDir(self, name):
        return self._children.get(name) is not None

    def hasFile(self, path):
        return path in self._paths

    @property
    def attach(self):
        return self._attach

    @attach.setter
    def attach(self, a):
        self._attach = a

    def checkout(self, name):
        tree = self._children.get(name)
        if not tree:
            tree = FileTree(name)
            self._children[name] = tree
            tree._par = self
        return tree

    def moveTo(self, tree):
        for path in self._paths:
            tree._paths.add(path)
        self._paths.clear()

    @property
    def paths(self):
        return self._paths

    def __contains__(self, path):
        return self.getTree(path) is not None

    def children(self):
        return [tree for tree in self._children.values()]

    @classmethod
    def getTreeFileCount(cls, tree):
        count = len(tree._paths)
        for sub in tree._children.values():
            count += cls.getTreeFileCount(sub)
        return count

    def fileCount(self):
        return FileTree.getTreeFileCount(self)

    def _buildFolder(self, folder):
        tree = self
        parts = folder.split(os.sep)
        for part in parts:
            sub = tree._children.get(part)
            if not sub:
                sub = FileTree(part)
                tree._children[part] = sub
                sub._par = tree
            tree = sub
        return tree

    def build(self, path):
        if os.path.isfile(path):
            tree = self._buildFolder(os.path.dirname(path))
            tree._paths.add(path)
            return tree
        else:
            return self._buildFolder(path)

    def removeChild(self, name):
        del self._children[name]

    def removeChildren(self):
        self._children.clear()

    def __contains__(self, path):
        if os.path.isdir(path):
            return self.getTree(path) is not None
        folder = os.path.dirname(path)
        tree = self.getTree(folder)
        return tree and path in tree._paths

    def _scanFolders(self, curPath, paths):
        curPath = os.path.join(curPath, os.sep, self._name)
        if not self._children:
            paths.append(curPath)
            return
        for child in self._children.values():
            child._scanFolders(curPath, paths)

    def getTreeFolders(self):
        folders = []
        self._scanFolders(self._name, folders)
        return folders

    def child(self, name):
        return self._children.get(name)

    def hasChild(self):
        return len(self._children)

    def hasFile(self):
        return len(self._paths)

    def prefix(self):
        names = []
        tree = self
        while tree._par:
            names.insert(0, tree._name)
            tree = tree._par
        return os.sep.join(names)
