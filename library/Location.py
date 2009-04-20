##########
# A location

from Database import DB
import pickle
from Logger import log

class Location:
    cache_by_id = {}
    cache_by_pos = {}

    ####
    # Load the object from a database cursor
    @staticmethod
    def _load(cur):
        try:
            cur.fetchone()
        except psycopg2.Error, dbex:
            log.error("Database exception:" + dbex)

        obj = pickle.loads(row[0])
        obj._id = id
        obj._changed = False
        return obj

    ####
    # Load the location by ID
    @staticmethod
    def load(lid):
        if lid in Location.cache_by_id:
            return Location.cache_by_id[lid]

        cur = DB.cursor()
        cur.execute('SELECT state FROM location WHERE id=%(id)s',
                    { 'id': lid } )

        return _load(cur)

    ####
    # Load the location by Position
    @staticmethod
    def load_by_pos(pos):
        if pos in Location.cache_by_pos:
            return Location.cache_by_pos[pos]

        cur = DB.cursor()
        cur.execute('SELECT state FROM location '
                    + 'WHERE x=%(x)s AND y=%(y)s AND layer=%(layer)s',
                    { 'x': pos.x,
                      'y': pos.y,
                      'layer': pos.layer }
                    )
        
        return _load(cur)

    ####
    # Save the object
    def save(self):
        if not self._changed:
            return

        state = pickle.dumps(self)

        cur = DB.cursor()
        cur.execute('UPDATE location SET state=%(state)s'
                    + ' WHERE id=%(id)s',
                    { 'id': self._id,
                      'state': state }
                    )

        self._changed = False

    ####
    # Create a new location
    def __init__(self):
        """Create a completely new location"""
        self.pos = Position(0, 0, 0)
        self.set_mapping()
        self._changed = True

    ####
    # Pickling (serialisation)
    def __getstate__(self, key):
        obj = {}
        for k in self.__dict__.keys():
            if not k startswith('_'):
                obj[k] = self.__dict__[k]

        # FIXME: Probably need a list of items to delete explicitly,
        # including r(), ur(), ul() and friends. pickle may have
        # trouble otherwise
        
        return obj

    ####
    # Make this object look more like a dictionary
    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    ####
    # Basic properties
    def power(self, name):
        if name in self:
            return self[name]
        
        return 0

    def set_mapping(self):
        pos = [ self.e, self.ne, self.nw, self.w, self.sw, self.se ]
        
        if self.flipped:
            self.r  = pos[(6+self.rotated) % 6]
            self.ur = pos[(5+self.rotated) % 6]
            self.ul = pos[(4+self.rotated) % 6]
            self.l  = pos[(3+self.rotated) % 6]
            self.ll = pos[(2+self.rotated) % 6]
            self.lr = pos[(1+self.rotated) % 6]
        else:
            self.r  = pos[(0+self.rotated) % 6]
            self.ur = pos[(1+self.rotated) % 6]
            self.ul = pos[(2+self.rotated) % 6]
            self.l  = pos[(3+self.rotated) % 6]
            self.ll = pos[(4+self.rotated) % 6]
            self.lr = pos[(5+self.rotated) % 6]

    def e(self):
        """Return the hex to the east of this one"""
        if self.warp_e != None:
            return load_loc(self.warp_e)
        pos = self.pos
        pos.x += 1
        return load_loc(pos)

    def w(self):
        if self.warp_w != None:
            return load_loc(self.warp_w)
        pos = self.pos
        pos.x -= 1
        return load_loc(pos)

    def ne(self):
        if self.warp_ne != None:
            return load_loc(self.warp_ne)
        pos = self.pos
        pos.y += 1
        return load_loc(pos)

    def nw(self):
        if self.warp_nw != None:
            return load_loc(self.warp_nw)
        pos = self.pos
        pos.x -= 1
        pos.y += 1
        return load_loc(pos)

    def se(self):
        if self.warp_se != None:
            return load_loc(self.warp_se)
        pos = self.pos
        pos.x += 1
        pos.y -= 1
        return load_loc(pos)

    def sw(self):
        if self.warp_se != None:
            return load_loc(self.warp_se)
        pos = self.pos
        pos.y -= 1
        return load_loc(pos)
