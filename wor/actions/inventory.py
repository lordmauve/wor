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
    group = 'inventory'
    message = u"You consume %(target)s."

    def do(self, actor, target):
        target.destroy()
        return self.message % {'target': target}
