########
# An item
# By default, all items are unique. Some items are "aggregate" and
# represent a block of otherwise identical things -- e.g. coins -- and
# can be combined and split (see AggregateItem).

import SerObject
import Actor
import Location
import Util

class Item(SerObject.SerObject):
    # Failure-rate (aka hazard) functions: return the probability
    # [0.0, 1.0) that this item will fail, given a lifetime of x
    @staticmethod
    def weibull(x, k, l):
        """Weibull failure function, with position l and shape k.  The
        mean of this distribution is l*GAMMA(1+1/k), where GAMMA is
        the gamma function."""
        return k/l * math.pow(x/l, k-1.0)

    # Default failure function is a mean life of 300, and equal
    # probability of failing on each use.
    break_profile = lambda life: weibull(life, 300.0, 1.0)

    @staticmethod
    def name_for(player):
        return "Item"

    @staticmethod
    def plural_for(player):
        return name_for(player) + 's'

    ####
    # Add the indices for saving this object
    def _save_indices(self):
        return { 'owner_type': self.owner_type,
                 'owner': self.owner,
                 'count': self.count,
                 'type': self.type }
    
    def owner(self):
        """Return the owner of this object, loading it if necessary"""
        if self._owner == None:
            if self.owner_type == 'Actor':
                self._owner = Actor.load(self.owner)
            elif self.owner_type == 'Location':
                self._owner = Location.load(self.owner)
            elif self.owner_type == 'Item':
                self._owner = Item.load(self.owner)
            else:
                pass
        return self._owner

    def power(self, name):
        return Util.default(self[name])

    def destroy(self):
        """Destroy this item, recycling it if necessary"""
        self.demolish()

    def try_break(self):
        """Test this item for breakage, and return True if it broke"""
        if random.random() < self.break_profile(self.lifetime):
            # Then we broke. You may cry.
            self.destroy()
            return True

        return False
