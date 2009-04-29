####
# Object to handle trigger events on property changes

class Trigger(object):
    def __init__(self, parent, key):
        self.parent = parent
        self.parent.register_trigger(self, key)

    def change(self, key, old, new):
        pass
