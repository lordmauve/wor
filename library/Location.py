##########
# A location

from Database import DB
import SerObject
from Logger import log

class Location(SerObject.SerObject):
    _table = 'location'
    cache_by_id = {}
    cache_by_pos = {}

    ####
    # Load the location by ID
    @staticmethod
    def load(lid):
        """Implement caching for loading a single location by ID"""
        if lid in Location.cache_by_id:
            return Location.cache_by_id[lid]
        return Location._load(lid)

    @staticmethod
    def load_by_pos(pos):
        """Load a location stack by position instead of by ID"""
        if pos in Location.cache_by_pos:
            return Location.cache_by_pos[pos]

        cur = DB.cursor()
        cur.execute('SELECT id FROM location '
                    + 'WHERE x=%(x)s AND y=%(y)s AND layer=%(layer)s '
                    + 'ORDER BY depth',
                    { 'x': pos.x,
                      'y': pos.y,
                      'layer': pos.layer }
                    )

        return Location._load(row[0])

    ####
    # Load the object from a database cursor
    @staticmethod
    def _load(lid):
        loc = Location.load_object(lid, Location._table)
        return loc

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

    def _save_indices(self):
        return { }

    def __getnewargs__(self):
        log.debug("__getnewargs__ called for location", self._id)
        self._type = "Location"
        return ()

    ####
    # Create a new location
    def __init__(self):
        """Create a completely new location"""
        super(Location, self).__init__()
        self.pos = Position(0, 0, 0)
        self.set_mapping()
        self._type = "Location"

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
