##########
# A location

class Location:
    def load(self, pos):
        pass

    def save(self):
        pass
    
    def __init__(self):
        self.pos = Position(0, 0, 0)
        self.set_mapping()

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
