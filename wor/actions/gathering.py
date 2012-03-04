import random
from .base import LocalAction

from wor.cost import Cost


class ForageAction(LocalAction):
    group = 'gathering'
    caption = u'Forage'
    message = u"You found %(loot)s."

    require = []

    items = []
    probability = 0.5

    failure_messages = [
        "You didn't find anything.",
        "Nada.",
        "You didn't have any luck.",
    ]

    def valid(self, actor, target):
        if not LocalAction.valid(self, actor, target):
            return False

        for item in self.require:
            if item not in actor.inventory:
                return False

        return True

    def do(self, actor, target):
        if random.random() > self.probability:
            i = actor.inventory.create(random.choice(self.items))
            return self.message % {'loot': i.description(), 'target': target}
        else:
            return random.choice(self.failure_messages)


class FishingAction(ForageAction):
    caption = u'Fish'
    require = ['tools.FishingRod']
    cost = Cost(ap=10)
    message = u"You caught %(loot)s."
