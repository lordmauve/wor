from base import Action
from wor.cost import Cost


class ActionAttack(Action):
    """An action in which a player attacks a target with the weapon
    he is holding."""

    group = 'combat'
    caption = u"Attack %(target)s"
    cost = Cost(ap=1)

    def valid(self, actor, target):
        weap = actor.held_item()

        # They could attack us...
        return weap and (actor.id is not target.id
            and target.is_combative(actor))

    def do(self, actor, target):
        actor.attack(target)
