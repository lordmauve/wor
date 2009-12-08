from wor.world.location import Location, Scenery


class Plain(Location):
	pass


class Hills(Location):
	move_ap = 6
	def power(self, name):
		"""Players can see further from higher up - during the day"""
		if name == 'sight' and self.region.get_time_of_day() != 'night':
			return 1
		return 0


class Village(Location):
	"""A small village"""


class Copse(Location):
	move_ap = 4


class Cliffs(Location):
	"""Chalk cliffs; these do not provide a actual barrier; just a cosmetic effect"""
	move_ap = 2


class Pond(Scenery):
	pass


class Road(Location):
	pass


class TradingPost(Location):
	pass


class Farm(Location):
	pass


class Wood(Location):
	move_ap = 10

class Mountain(Scenery):
	pass

class Peak(Scenery):
	pass
