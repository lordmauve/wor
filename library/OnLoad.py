##########
# "Aspect" class to provide infrastructure for members of SerObjects
# that want to be called on load events.

class OnLoad(object):
    def __setstate__(self, state):
        for k, v in state.iteritems():
            self.__dict__[k] = v
        if 'parent' in self.__dict__:
            if '_on_load_objects' not in self.parent.__dict__:
                self.parent._on_load_objects = []
            self.parent._on_load_objects.append(self)
