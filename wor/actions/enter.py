from base import Action
from Cost import Cost

class ActionEnter(Action):
	cost = Cost(ap=1)
	group = 'movement'

	def __init__(self, actor, building):
		super(ActionEnter, self).__init__(actor)
		self.building = building

	def get_uid(self):
		return 'enter-%d' % self.building.id

	def get_caption(self):
		return "Enter %s" % self.building.name

	def action(self):
		self.actor.position = self.building.get_entry_point()


class ActionExit(ActionEnter):
	cost = Cost(ap=1)
	group = 'movement'

	def get_uid(self):
		return 'exit-%d' % self.building.id

	def get_caption(self):
		return "Leave %s" % self.building.name

	def action(self):
		self.actor.position = self.building.position
