##########
# A location

class Location:
    def load(self, pos):
        pass

    def save(self):
        pass
    
    def __init__(self):
        self.pos = Position(0, 0, 0)

    def power(self, name):
        if name in self:
            return self[name]
        
        return 0
