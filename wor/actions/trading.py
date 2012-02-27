from wor.actions.base import Action, ItemField
from wor.items.base import Item

from wor.cost import Cost


class ActionBuy(Action):
    cost = Cost(gp=1)
    caption = 'Buy'
    item = None

    def get_item(self):
        return Item.get_class(self.item)

    def get_parameters(self):
        return ['Buy', ItemField(self.get_item())]

    def valid(self, actor, target):
        return actor.pos == target.pos

    def do(self, actor, target):
        i = actor.inventory.create(self.item)
        return "You purchase %s." % i.description()
