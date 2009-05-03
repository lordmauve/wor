##########
# Generic actor: covers players, NPCs, monsters

import SerObject
import Util
import pickle
import copy
import psycopg2

class Actor(SerObject.SerObject):
    ####
    # Creating a new object
    def __init__(self):
        """Create a completely new actor"""
        super(Actor, self).__init__()
        self.messages = "You spring into the world, fresh and new!"

    ####
    # Basic properties of the object
    def loc(self):
        """Return the Location (or Road for monsters) that we're stood on"""
        if self._loc == None:
            self._loc = load_location(self.loc)
        return self._loc

    def held_item(self):
        """Return the item(s) currently held by the actor"""
        pass

    def equipment(self):
        """Return an iterator over the equipment currently worn by the actor"""
        pass

    def power(self, name):
        """Compute the effective power of a property"""
        # FIXME: Implement caching of power calculations here
        pow = 0

        # Start with intrinsics
        if name in self:
            pow += Util.default(self[name])

        # Equipment held
        pos += self.held_item().power(name)

        # Equipment worn
        for item in self.equipment():
            pos += item.power(name)

        # Location
        pos += self.loc().power(name)

        return pow

    ####
    # Administration
    def message(self, message):
        """Write a message to the actor's message log"""
        self.messages += message + "\n"
        if len(self.messages > 1024):
            self.messages = self.messages[-1024:]
        self._changed = True

    ####
    # Actions infrastructure: Things the player can do to this actor
    def actions(self):
        """Create and return a hash of all possible actions this
        player might perform"""
        return {}

    def perform_action(self, actid, req):
        """Perform an action as requested. req is a mod_python request
        object"""
        actions = self.actions()
        actions[actid].perform(req)
