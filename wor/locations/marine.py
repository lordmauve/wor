from wor.world.location import Location
from wor.actions.gathering import FishingAction

class Pontoon(Location):
    fish = FishingAction(
        items=[
            'food.Salmon',
            'food.Perch',
            'food.Carp'
        ]
    )


class Sea(Location):
    title = "Sea"
    def can_enter(self, act):
        return False

class Lake(Sea):
    title = "Lake"


class River(Sea):
    """A river"""


class Shallows(Sea):
    """Shallow sea water. Swimmable perhaps?"""
