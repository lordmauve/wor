##########
# Generic actor: covers players, NPCs, monsters

from Database import DB
import pickle
import copy
import psycopg2

####
# Construction and loading
def load_actor(id, table):
    """Get the actor with the given id"""
    try:
        cur = DB.cursor()
        cur.execute('SELECT state FROM ' + table
                    + ' WHERE id=%(id)s',
                    { 'id': id }
                    )
        row = cur.fetchone()
    except psycopg2.Error, dbex:
        sys.stderr.write("Database exception:" + dbex + "\n")
        return Actor(0)

    obj = pickle.loads(row[0])
    obj._id = id
    obj._changed = False
    return obj

class Actor(object):
    ####
    # Saving the object
    def save(self):
        if not self._changed:
            return

        state = pickle.dumps(self)

        cur = DB.cursor()
        sql = 'UPDATE ' + self.table + ' SET state=%(state)s WHERE id=%(identity)s'
        mapping = { 'identity': self._id,
                    'state': state }
        cur.execute(sql, mapping)

        self._changed = False

    def __init__(self):
        """Create a completely new actor"""
        self.messages = "You spring into the world, fresh and new!"
        self._changed = True

    ####
    # Pickling (serialisation)
    def __getstate__(self):
        # Shallow-create a new dictionary based on our current one,
        # but leave out all the properties that start with _
        obj = {}
        for k in self.__dict__.keys():
            if not k.startswith('_'):
                obj[k] = self.__dict__[k]
        return obj

    ####
    # Property access: make this object look more like a dictionary
    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    ####
    # Basic properties of the object
    def loc(self):
        """Return the Location (or Road for monsters) that we're stood on"""
        if '_loc' not in self.__dict__:
            self._loc = load_location(self.loc)
        return self._loc

    def held_item(self):
        """Return the item(s) currently held by the actor"""
        if '_item' not in self.__dict__:
            self._item = load_item(self.loc)
        return self._item

    def equipment(self):
        """Return an iterator over the equipment currently worn by the actor"""
        pass

    def power(self, name):
        """Compute the effective power of a property"""
        # FIXME: Implement caching of power calculations here
        pow = 0

        # Start with intrinsics
        if name in self:
            pow += self[name]

        # Equipment held
        pos += self.held_item().power(name)

        # Equipment worn
        for item in self.equipment():
            pos += item.power(name)

        # Location
        pos += self.loc().power(name)

        return pow

    def set_prop(self, name, value):
        self[name] = value
        self._changed = True

    def change_prop(self, name, diff, min=0, max=None):
        newval = 0
        if name in self:
            newval = self[name]
        newval += diff
        newval = max(newval, min)
        if max != None:
            newval = min(newval, max)
        self._changed = True
        return newval

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
