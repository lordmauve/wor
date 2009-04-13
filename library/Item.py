########
# An item
# By default, all items are unique. Some items are "aggregate" and
# represent a block of otherwise identical things -- e.g. coins -- and
# can be combined and split (see AggregateItem).

class Item(object):
    def __init__(self):
        pass

    def load(id):
        """Get the item with the given id"""
        # FIXME: Caching here
        try:
            cur = DB.db.cursor()
            cur.execute('SELECT state FROM item'
                        + ' WHERE id=%(id)s',
                        { 'id': id }
                        )
            row = cur.fetchone()
            obj = pickle.loads(row[0])
            obj._changed = False
            return obj
        except:
            return None

    def save(self):
        if not self._changed:
            return

        cur = DB.db.cursor()
        cur.execute('UPDATE ' + table
                    + ' SET state = %(state)s WHERE id = %(id)s',
                    { 'id': self.id,
                      'state': pickle.dumps(self) }
                    )

        self._changed = False

    def __init__(self, id):
        """Create a completely new actor"""
        self.id = id
        self.state = {}

    ####
    # Pickling (serialisation)
    def __getstate__(self):
        return self.state

    def __setstate__(self, state):
        self.state = state
        self._container = None

    ####
    # Basic properties
    def container(self):
        # A container can be an actor, another item (bag, pack-horse),
        # or a location.
        if self._container = None:
            pass
