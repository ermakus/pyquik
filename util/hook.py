class Hook(object):

    def __init__(self):
        self.__handlers = []

    def __iadd__(self, handler):
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.__handlers.remove(handler)
        return self

    def __call__(self, *args, **keywargs):
        for handler in self.__handlers:
            handler(*args, **keywargs)

class ReadyHook(Hook):

    def __init__(self, count=0, once=True):
        Hook.__init__(self)
        self.count = count
        self.fired = False
        self.once = once

    def start(self):
        self.count += 1

    def ready(self):
        self.count -= 1
        if self.count < 0:
            raise Exception("Ready hook is negative")

    def __call__(self,*args,**kwargs):
        if self.count == 0:
            if not self.fired:
                self.fired = self.once
                Hook.__call__(self,*args,**kwargs)
