class BehaviourStatic(object):	
	def update(self, mob):
		pass


class BehaviourAimlessWander(object):	
	def update(self, mob):
		l = mob.loc()
		dirs = []
		# build a list of permissible directions around mob
		for i in range(0, 6):
			n = l.local_directions_name[i]
			if l.could_go(player, n):
				dirs.append(n)

		# select one at random
		d = random.choice(dirs)
		dest = l.local_directions[d](l)
		mob.position = dest



