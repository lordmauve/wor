from wor.world.location import Location


class Plain(Location):
	pass


class Hills(Location):
	move_ap = 6
	def power(self, name):
		"""Players can see further from higher up"""
		if name == 'sight':
			return 1
		return 0


class Village(Location):
	"""A small village"""
