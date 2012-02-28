import random
from base import LocalAction


class ForageAction(LocalAction):
    group = 'gathering'
    caption = u'Forage'
    message = u"You consume the %s."

    items = []
    probability = 0.5

    failure_messages = [
        "You didn't find anything.",
        "Nada.",
        "You didn't have any luck.",
    ]

    def do(self, actor, target):
        if random.random() > self.probability:
            i = actor.inventory.create(random.choice(self.items))
            return "You found %s." % i.description()
        else:
            return random.choice(self.failure_messages)
