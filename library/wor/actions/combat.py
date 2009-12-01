from base import TargettedAction
from Cost import Cost


class ActionAttack(TargettedAction):
	"""An action in which a player attacks a target with the weapon
	he is holding."""

	group = 'combat'
	caption = u"Attack %s"

	def __init__(self, player, target, cost=Cost(ap=1)):
		super(ActionAttack, self).__init__(player, target)
		self.target = target
		self.cost = cost

	def action(self, data):
		self.player.attack(self.target)
