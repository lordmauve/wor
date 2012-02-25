import re
from wor.db import db
from base import WorldObject

from wor.actions.enter import ActionEnter

class Building(WorldObject):
    """Buildings are enterable objects.

    We will instance a new region that this object "contains" when
    the instance is created.
    """
    def __init__(self, name, internal_region=None, entry_point=None):
        self.name = name
        if internal_region is None:
            self.internal_region = self.create_region()
        else:
            self.internal_region = internal_region

        self.entry_point = entry_point    # entry point to the region

    def get_entry_point(self):
        from Position import Position
        return self.entry_point or Position(0, 0, self.internal_region.name)

    def create_region(self):
        world = db.world()
        key = world.find_region_key(self.name)
        region = world.create_region(key, self.name)
        region.parent_building = self
        return region

    def external_actions(self, player):
        return [
            ActionEnter(player, self)
        ]


class Pub(Building):
    """A drinking establishment."""
    def get_description(self):
        n = self.internal_region.num_actors()
        if n == 0:
            d = "It's oddly silent. You wonder if it's closed."
        elif n < 4:
            d = "Currently looking pretty empty."
        elif n < 10:
            d = "There's a small crowd inside."
        else:
            d = "The sound of chatter and laughter spills out from inside."
        if self.description:
            return self.description + '\n\n' + d
        return d

    def create_region(self):
        from wor.locations import interior
        region = super(Pub, self).create_region()
        region.set_location((0,0), interior.Pub())
        return region

