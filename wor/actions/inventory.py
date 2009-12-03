from base import Action
from Cost import Cost

class ActionChangeItem(Action):
	group = 'inventory'

	def __init__(self, player):
		super(ActionChangeItem, self).__init__(player)

	def get_uid(self):
		return 'change_item'

	def get_caption(self):
		return u"Change item"

	def action(self, data):
		self.actor.change_item_action(data)
