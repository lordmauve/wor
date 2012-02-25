from base import Action, ActionFailed, IntegerField
from Cost import Cost

class ActionChangeItem(Action):
    group = 'inventory'

    def __init__(self, player):
        super(ActionChangeItem, self).__init__(player)

    def get_uid(self):
        return 'change_item'

    def get_caption(self):
        return u"Change item"

    def get_parameters(self):
        return [IntegerField('id')]

    def action(self, id):
        try:
            item = self.actor.inventory[id]
        except KeyError:
            raise ActionFailed('Item not found.')
        self.actor.set_held_item(item)
