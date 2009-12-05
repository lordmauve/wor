from wor.world.location import Location, InteriorLocation


class Floorboards(InteriorLocation):
	"""Wooden floorboards."""


class Pub(InteriorLocation):
	"""Pub Tables."""

class Hearth(Location):
	def can_enter(self, actor):
		return False
	
