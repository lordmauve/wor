#########
# Serialisable object
# This is the base object for all objects that might end up in the database

from Database import DB
import pickle
import copy
import psycopg2
import Util

####
# A serialisable object
class SerObject(object):
    _picklables = [ 'value_triggers' ]
    
    ####
    # Loading the object by ID from the database
    @staticmethod
    def load_object(id, table, allprops=False):
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

        if row == None:
            return None

        obj = pickle.loads(row[0])
        #obj.value_triggers = Util.default(obj['value_triggers'], {})

        if allprops:
            # Fetch all properties of the object immediately (rather
            # than on demand)
            try:
                cur.execute('SELECT key, type, ivalue, fvalue, tvalue, bvalue'
                            + ' FROM ' + table + '_properties'
                            + ' WHERE ' + table + '_id=%(id)s',
                            { 'id': id }
                            )
                row = cur.fetchone()
                while row != None:
                    obj._set_prop_from_row(row)
                    row = cur.fetchone()
            except psycopg2.Error, dbex:
                sys.stderr.write("Database exception:" + dbex + "\n")
                return None
        
        obj._id = int(id)
        obj._setup()
        return obj

    def _set_prop_from_row(self, row):
        """Set an object property from a DB row. Does not set the
        _changed property."""
        if row[1] == 'i':
            self.__dict__[row[0]] = row[2]
        elif row[1] == 'f':
            self.__dict__[row[0]] = row[3]
        elif row[1] == 't':
            self.__dict__[row[0]] = row[4]
        elif row[1] == 'b':
            self.__dict__[row[0]] = (row[2] == 1)
        elif row[1] == 'p':
            self.__dict__[row[0]] = pickle.loads(row[5])

    ####
    # Saving the object to the database
    def save(self):
        """Save to the database the parts of the object that have changed"""
        if not self._changed:
            return
        if self._deleted:
            cur = DB.cursor()
            cur.execute('DELETE FROM ' + self._table
                        + ' WHERE id=%(id)s',
                        { 'id': self._id })
            self._changed = False
            return

        # First, save the object itself plus its metadata
        state = pickle.dumps(self, -1) # Use the highest pickle
                                       # protocol we can

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
        cur.execute(sql, idx)

        # Secondly, we iterate through the elements of the object that
        # have changed and save them
        params = { 'id': self._id }
            
        for key in self._changed_props:
            if key in self._picklables:
                continue
            if self.__dict__[key] == None:
                continue
            
            params['key'] = key
            params['value'] = self.__dict__[key]

            typ = type(self.__dict__[key])
            if typ is int:
                params['type'] = 'i'
                value_field = 'ivalue'
            elif typ is float:
                params['type'] = 'f'
                value_field = 'fvalue'
            elif typ is str or typ is unicode:
                params['type'] = 't'
                value_field = 'tvalue'
            elif typ is bool:
                params['type'] = 'b'
                value_field = 'ivalue'
            else:
                params['type'] = 'p'
                value_field = 'bvalue'
                params['value'] = psycopg2.Binary(
                    pickle.dumps(self.__dict__[key], -1)
                    )
            
            cur.execute('SAVEPOINT update1')
            try:
                sql = 'INSERT INTO ' + self._table + '_properties'
                sql += ' (player_id, key, type, ' + value_field + ')'
                sql += 'VALUES (%(id)s, %(key)s, %(type)s, %(value)s)'
                cur.execute(sql, params)
            except psycopg2.Error, ex:
                cur.execute('ROLLBACK TO SAVEPOINT update1')
                cur.execute('UPDATE ' + self._table + '_properties'
                            + ' SET ' + value_field + ' = %(value)s,'
                            + '     type = %(type)s'
                            + ' WHERE player_id = %(id)s'
                            + '   AND key = %(key)s',
                            params)
            else:
                cur.execute('RELEASE SAVEPOINT update1')
        
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
            if not k.startswith('_') and k in self._picklables:
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
        """Used to implement [] subscripting, for string-based
        property access. Also copes with on-demand loading of
        properties. Returns None if not found."""
        if key not in self.__dict__:
            if not self._demand_load_property(key):
                self.__dict__[key] = None
        return self.__dict__[key]

    def __getattr__(self, key):
        """Does on-demand loading of properties from the DB. Raises an
        error if not found"""
        if key not in self.__dict__:
            if not self._demand_load_property(key):
                raise AttributeError()
        return self.__dict__[key]

    def _demand_load_property(self, key):
        cur = DB.cursor()
        cur.execute('SELECT key, type, ivalue, fvalue, tvalue, bvalue'
                    + ' FROM ' + self._table + '_properties'
                    + ' WHERE ' + self._table + '_id = %(id)s'
                    + '   AND key = %(key)s',
                    { 'id': self._id,
                      'key': key })
        row = cur.fetchone()
        if row != None:
            self._set_prop_from_row(row)
            return True
        else:
            return False

    # Yes, these next two are identical. I'm not merging them because
    # I'm nervous about the precise semantics -HRM
    def __setitem__(self, key, value):
        """Used to set a value via [] subscripting, for string-based
        property access"""
        if key[0] != '_':
            # Get the original value of the attribute
            old = 0
            if key in self.__dict__:
                old = self.__dict__[key]
            # Set the new value of the attribute
            self.__dict__[key] = value
            # Call the triggers
            self.__call_triggers(key, old, value)
            self._changed = True
            self._changed_props.add(key)
        else:
            # Set the new value of the attribute
            self.__dict__[key] = value

    def __setattr__(self, key, value):
        """Used to set a value via obj.key = value"""
        if key[0] != '_':
            # Get the original value of the attribute
            old = 0
            if key in self.__dict__:
                old = self.__dict__[key]
            # Set the new value of the attribute
            self.__dict__[key] = value
            # Call the triggers
            self.__call_triggers(key, old, value)
            self._changed = True
            self._changed_props.add(key)
        else:
            # Set the new value of the attribute
            self.__dict__[key] = value

    def __call_triggers(self, key, old, new):
        """Iterate through the triggers, if there are any"""
        for t in self.value_triggers.get(key, []):
            t.change(key, old, new)

    def register_trigger(self, trigger, key):
        """Called by a Trigger to register it with us as interested in
        particular value change events"""
        if key not in self.value_triggers:
            self.value_triggers[key] = []
        self.value_triggers[key].append(trigger)

    def unregister_trigger(self, trigger, key):
        """Called by a trigger to unregister itself"""
        self.value_triggers[key].remove(trigger)

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
        self._setup()
        self.value_triggers = {}

    def _setup(self):
        """Called after __init__ or after load()"""
        self._changed = False
        self._deleted = False
        self._changed_props = set()

    ####
    # Destruction
    def demolish(self):
        self._deleted = True
