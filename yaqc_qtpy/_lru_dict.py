from collections import OrderedDict


class LRUDict(OrderedDict):
    """LRU Cache"""

    def __init__(self, maxsize=128, cleanup=None):
        super().__init__(self)
        self.maxsize = maxsize
        self.cleanup = cleanup

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.move_to_end(key)
        if len(self) > self.maxsize:
            val = self.popitem(0)[1]
            if self.cleanup:
                self.cleanup(val)
            val.deleteLater()

    def __getitem__(self, key):
        val = super().__getitem__(key)
        try:
            self.move_to_end(key)
        except KeyError:
            # Happens when popitem is called
            pass
        return val
