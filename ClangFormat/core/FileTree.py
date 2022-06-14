import os


class FileTree:

    def __init__(self, name):
        self._paths = set()
        self._modified = set()
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

    @property
    def modified(self):
        return self._modified

    def __contains__(self, path):
        return self.getTree(path) is not None

    def children(self):
        return [tree for tree in self._children.values()]

    @classmethod
    def getTreeFileCount(cls, tree, modified=False):
        count = len(tree._paths if not modified else tree._modified)
        for sub in tree._children.values():
            count += cls.getTreeFileCount(sub, modified)
        return count

    def fileCount(self, modified=False):
        return FileTree.getTreeFileCount(self, modified)

    def _buildFolder(self, folder):
        tree = self
        parts = folder.split(os.sep)
        for part in parts:
            if not part: continue
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

    def child(self, name):
        return self._children.get(name)

    def hasChild(self):
        return len(self._children)

    def hasFile(self):
        return len(self._paths)

    def cwd(self):
        names = []
        tree = self
        while tree._par:
            names.insert(0, tree._name)
            tree = tree._par
        return os.sep.join(names)

    def match(self, path):
        tree = self
        parts = path.split(os.sep)
        for part in parts:
            if not part: continue
            sub = tree.child(part)
            if not sub: break
            tree = sub
        else:
            return tree, True
        return tree, False

    def __repr__(self):
        data = {}
        data['name'] = self._name
        data['children'] = self._children
        data['parent'] = self.parent.name if self.parent else ''
        return str(data)

    def markModified(self, path):
        if path in self._paths:
            self._modified.add(path)
        elif os.path.normcase(os.path.dirname(path)) == os.path.normcase(
                self.cwd()):
            self._paths.add(path)
            self._modified.add(path)
        else:
            return False
        return True

    def newPath(self, path):
        if path not in self._paths:
            self._paths.add(path)
            self._modified.add(path)
