##########
# Area: a region of landscape

class Area:
	def __init__(self):
		pass

	def covered(self, pos):
		"""Return true if the position pos is within the named area"""
		pass

	def area_to_global(self, pos):
		"""Return the "global" position of pos in this area. Does not
		check the "covered" state."""
		return pos

	def global_to_area(self, pos):
		"""Return the "local" position of the global coord pos in this area."""
		return pos
