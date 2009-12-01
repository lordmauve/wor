from base import Action
from Cost import Cost


class ActionMove(Action):
	group = 'movement'

	def __init__(self, actor, direction, cost=Cost(ap=1)):
		super(ActionMove, self).__init__(actor)
		self.direction = direction
		self.cost = cost

	def get_uid(self):
		return 'move-' + self.direction

	def get_caption(self):
		return 'Move ' + self.direction.upper()

	def action(self, data):
		dest = getattr(self.actor.loc(), self.direction.lower())()
		assert dest
		self.actor.move_to(dest)

