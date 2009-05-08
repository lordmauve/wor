##########
# A location

from Database import DB
from SerObject import SerObject
from Logger import log

class Location(SerObject):
    _table = 'location'
    cache_by_id = {}
    cache_by_pos = {}

    ####
    # Load the location
    @classmethod
    def load_by_pos(cls, pos, allprops=False):
        """Load a complete location stack by position"""
        rpos = repr(pos)
        if rpos in Location.cache_by_pos:
            return Location.cache_by_pos[rpos]

        cur = DB.cursor()
        cur.execute('SELECT id, state FROM location '
                    + 'WHERE x=%(x)s AND y=%(y)s AND layer=%(layer)s '
                    + 'ORDER BY overlay',
                    { 'x': pos.x,
                      'y': pos.y,
                      'layer': pos.layer }
                    )
        row = cur.fetchone()
        location = None
        while row != None:
            # Load the overlay
            tmploc = cls._load_from_row(row, allprops)
            # Set up a doubly-linked list
            tmploc._underneath = location
            if location != None:
                location._above = tmploc
            # Push the underlying location down
            location = tmploc
            row = cur.fetchone()

        return location

    @classmethod
    def _cache_object(cls, obj):
        rpos = repr(obj.pos)
        cls.cache_by_pos[rpos] = obj

    def _save_indices(self):
        inds = super(Location, self)._save_indices()
        inds['x'] = self.pos.x
        inds['y'] = self.pos.y
        inds['layer'] = self.pos.layer
        inds['overlay'] = self.overlay
        return inds

    ####
    # Create a new location
    def __init__(self, pos):
        """Create a completely new location"""
        super(Location, self).__init__()
        self.pos = pos
        self.overlay = 0
        self.set_mapping()
        
        self._cache_object(self)

    ####
    # Stack management
    def deoverride(self):
        """Unhook this location (overlay) from the stack, and remove
        it from the database."""
        self._underneath._above = self._above
        if self._above != None:
            self._above._underneath = self._underneath
        self._deleted = True

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
