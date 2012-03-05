from base import Action, PersonalAction, ActionFailed, IntegerField


class ActionChangeItem(PersonalAction):
    group = 'inventory'
    caption = u"Change item"

    def get_parameters(self):
        return [IntegerField('id')]

    def do(self, actor, target, id):
        try:
            item = actor.inventory[id]
        except KeyError:
            raise ActionFailed('Item not found.')
        actor.set_held_item(item)


class ConsumeAction(Action):
    """Consume an item from the player's inventory."""

    group = 'inventory'
    caption = u"Consume"
    message = u"You consume %(target)s."

    def do(self, actor, target):
        inst = actor.inventory.split_or_remove(target)
        msg = self.message % {'target': inst}
        inst.destroy()
        return msg
