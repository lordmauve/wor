from wor.world.location import Location
from wor.npcs.townspeople import Trader
from wor.actions.admin import ActionSpawn

class Town(Location):
    """Town"""
    spawn_trader = ActionSpawn(
        mob=Trader
    )


class Street(Location):
    """Town street"""
    spawn_trader = ActionSpawn(
        mob=Trader
    )


class Church(Location):
    """A church"""
