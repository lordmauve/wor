from wor.world.location import Location


class Sea(Location):
	title = "Sea"
	def can_actor_enter(self, act):
		return False

class Lake(Sea):
	title = "Lake"


class River(Sea):
	"""A river"""


class Shallows(Sea):
	"""Shallow sea water. Swimmable perhaps?"""
