from base import Action
from wor.cost import Cost


class ActionEnter(Action):
    cost = Cost(ap=1)
    group = 'movement'
    caption = u"Enter"

    def do(self, actor, target):
        actor.position = target.get_entry_point()


class ActionExit(ActionEnter):
    cost = Cost(ap=1)
    group = 'movement'
    caption = "Leave %s"

    def get_caption(self, target):
        return self.caption % target.region.title

    def do(self, actor, target):
        actor.position = target.region.parent_building.position
