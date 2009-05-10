#######
# A simple single-button action

from Action import Action
from Logger import log

class SimpleAction(Action):
    def __init__(self, parent, uid="use", cap="Use", ap=1,
                 message="",
                 failmessage="You can't do that.",
                 action=lambda x: None,
                 ):
        super(SimpleAction, self).__init__(parent)
        self.cap = cap
        self.ap = ap
        self.message = message
        self.action = action
        self.uid = uid
        self.parent = parent
        log.debug("SimpleAction: " + str(type(self.parent._id)))
        self.fuid = "%s.%d.%s" % (self.parent.type(), self.parent._id, self.uid)

    def display(self):
        return "%(message)s <button onclick='act_simple(\"%(fuid)s\")'>%(cap)s (%(ap)d AP)</button>" % self.__dict__

    def perform(self, req):
        if not self.valid():
            self.parent.message(failmessage)
            return False

        return self.action(self.parent)
