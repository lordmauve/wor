from base import Action
from wor.cost import Cost


class ActionMove(Action):
    group = 'movement'
    direction = 'l'
    cost = Cost(ap=1)

    @property
    def caption(self):
        return 'Move ' + self.direction.upper()

    def do(self, actor, target):
        dest = getattr(actor.loc(), self.direction.lower())()
        assert dest
        actor.move_to(dest)

