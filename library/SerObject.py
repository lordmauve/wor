#########
# Serialisable object
# This is the base object for all objects that might end up in the database

from Database import DB
import pickle
import copy
import psycopg2

####
# A serialisable object
class SerObject(object):
    ####
    # Loading the object by ID from the database
    @staticmethod
    def load_object(id, table):
        """Get the SerObject with the given id from the given table"""
        try:
            cur = DB.cursor()
            cur.execute('SELECT state FROM ' + table
                        + ' WHERE id=%(id)s',
                        { 'id': id }
                        )
            row = cur.fetchone()
        except psycopg2.Error, dbex:
            sys.stderr.write("Database exception:" + dbex + "\n")
            return None

        obj = pickle.loads(row[0])
        obj._id = int(id)
        obj._changed = False
        return obj

    ####
    # Saving the object to the database
    def save(self):
        if not self._changed:
            return

        state = pickle.dumps(self, -1) # Use the highest pickle
                                       # protocol we can: must be at
                                       # least 2, to enable
                                       # __getnewargs__()

        sql = 'UPDATE ' + self._table + ' SET state=%(state)s'
                    
        # We find out what additional indices we need to write to the
        # DB, and construct some SQL for them
        idx = self._save_indices()
        for iname in idx.iterkeys():
            sql += ', %(iname)s=%%(%(iname)s)s' % { 'iname': iname }

        sql += ' WHERE id=%(identity)s'

        # Add in the required parameters of identity and state
        idx['identity'] = self._id
        idx['state'] = psycopg2.Binary(state)

        # Update the DB
        cur = DB.cursor()
        print sql
        print idx
        cur.execute(sql, idx)
        print "Success"
        
        self._changed = False

    def _save_indices(self):
        """Return a dict of DB field names and values to write as
        additional indexes to the database"""
        return { }

    ####
    # Pickling (serialisation and deserialisation)
    def __getstate__(self):
        """Save this object to a pickled state"""
        # Shallow-create a new dictionary based on our current one,
        # but leave out all the properties that start with _
        obj = {}
        for k in self.__dict__.keys():
            if not k.startswith('_'):
                obj[k] = self.__dict__[k]
        return obj

    def __setstate__(self, state):
        """Load an object from a pickled state"""
        for k, v in state.iteritems():
            self.__dict__[k] = v
        # Anything (member objects) which wants to be called after
        # load gets called here
        if '_onload_objects' in self.__dict__:
            for obj in self['_on_load_objects']:
                obj._on_load()
            del(self['_on_load_objects'])

    ####
    # Property access. Not directly related to object serialisation,
    # but needed by everything.
    def __getitem__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        # I'm not convinced the next two lines are a good idea -HRM
        #if '_'+key in self.__dict__:
        #    return self.__dict__['_'+key]
        return None

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    ####
    # Construction
    def __init__(self):
        # Create a new record in the database for this object and get
        # its ID
        cur = DB.cursor()
        cur.execute('SELECT nextval(\'player_id_seq\');')
        row = cur.fetchone()
        self._id = row[0]
        cur.execute('INSERT INTO ' + self._table
                    + ' (id, state) VALUES (%(id)s, NULL)',
                    { 'id': self._id })
        print "New SerObject ID =", self._id
        self._changed = True
