from wor.world.location import Location, InteriorLocation, Scenery


class Floorboards(InteriorLocation):
	"""Wooden floorboards."""


class Pub(InteriorLocation):
	"""Pub Tables."""


class Hearth(Scenery):
	description = "A warm glow radiates from the fireplace that makes you feel at home."
	

class Column(Scenery):
	"""A stone column"""


class Fountain(Scenery):
	description = "Try to ignore it if you're desperate to go to the toilet."


class Flowers(Scenery):
	description = "These fragrant and exotic blooms are a joy to look at."""


class Courtyard(Scenery):
	"""Flagstones"""


class Rooftop(Scenery):
	"""Roofing tiles"""
