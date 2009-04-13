#########
# Representative of a coordinate: also includes orientation

class Position:
    North = 0
    East = 0
    South = 0
    West = 0
    
    def __init__(self, x, y, layer, up=North):
        self.x = x
        self.y = y
        self.layer = layer
        self.up = up
