from wor.world.location import Location


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
