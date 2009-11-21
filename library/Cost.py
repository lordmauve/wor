class Cost(object):
	"""A cost to perform an action, chargeable to a user."""
	def __init__(self, ap=0, hp=0, gp=0):
		self.ap = ap
		self.hp = hp
		self.gp = gp

	def __str__(self):
		vs = []

		if self.ap:
			vs += ['%d AP' % self.ap]
		if self.hp:
			vs.append('%d HP' % self.hp)
		if self.gp:
			vs.append('%d GP' % self.gp)

		return ', '.join(vs)

	def can_afford(self, player):
		return (player.has('GoldPiece', self.gp)
				and player.hp > self.hp
				and player.ap > self.ap)

	def charge(self, player):
		player.ap -= self.ap
		player.hp -= self.hp
		if self.gp:
			player.take_items('GoldPiece', self.gp)
