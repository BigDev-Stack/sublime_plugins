import threading

class Singleton:
    __instanceLock = threading.RLock()
    __instances = {}

    def __init__(self, cls):
        self.cls = cls

    def __call__(self, *args, **kwargs):
        with Singleton.__instanceLock:
            instance = Singleton.__instances.get(self.cls)
            if instance is None:
                instance = self.cls(*args, **kwargs)
                Singleton.__instances[self.cls] = instance
        return instance
