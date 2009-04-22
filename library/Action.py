######
# An action: something that the user can be invited to do
# There should be few cases where this class is directly subclassed.
# Use e.g. SimpleAction as a base instead.

class Action(object):
    def __init__(self, parent):
        self.parent = parent

    def valid(self):
        return True

    def display(self):
        return "Action"

    def perform(self, req):
        pass
