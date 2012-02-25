from wor.actions.base import Action, ItemField
from wor.items.base import Item

from wor.cost import Cost


class ActionBuy(Action):
    cost = Cost(gp=1)
    caption = 'Buy'

    def __init__(self, actor, seller, item, price):
        super(ActionBuy, self).__init__(actor)
        self.seller = seller
        self.item = item
        self.price = price
        self.cost = Cost(gp=price)

    def get_uid(self):
        return 'buy-%s-from-%d' % (self.item, self.seller.id)

    def get_item(self):
        return Item.get_class(self.item)

    def get_parameters(self):
        return ['Buy', ItemField(self.get_item())]

    def action(self):
        i = self.actor.inventory.create(self.item)
        return "You purchase %s." % i.description()
