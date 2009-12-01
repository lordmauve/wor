from persistent import Persistent
from persistent.mapping import PersistentMapping
from persistent.list import PersistentList

from BTrees.IOBTree import IOBTree
from BTrees.OOBTree import OOBTree

from Position import Position
from wor.world.location import Location


class Region(Persistent):
	"""A region is a group of locations that form a unit.

	Regions are not physically connected to one another: transferring between regions
	requires warps or other devices.
	
	"""
	def __init__(self, name, title=None):
		self.name = name  # the internal name of the region
		self.title = title # the display title of the region

		self.world = None

		self.locations = PersistentMapping() # Position has to have a total order for this
		self.actors = PersistentMapping()

		self.set_location((0,0), Location('Centre of ' + self.get_title()))

	def __unicode__(self):
		"""Return the title, or fall back to the internal name if unset"""
		return self.title or self.name.title()

	get_title = __unicode__

	def __getitem__(self, coords):
		"""Return the location at the position indicated by coords"""
		return self.locations[coords]

	def set_location(self, coords, loc):
		self.locations[coords] = loc
		x, y = coords
		loc.region = self
		loc.pos = Position(x, y, self.name)

	def get_actors_at(self, pos):
		return list(self.actors.get(pos, []))

	def _remove_actor(self, actor):
		"""Removes an actor from its current location"""
		self.actors[actor.position].remove(actor)
		if len(self.actors[actor.position]) == 0:
			del(self.actors[actor.position])

	def _add_actor(self, actor, dest):
		"""Adds an actor at the given position"""
		self.actors.setdefault(dest, PersistentList()).append(actor)

	def actor_enter(self, actor, dest):
		"""Called when an actor enters from another region"""
		self._add_actor(actor, dest)
	
	def actor_leave(self, actor):
		"""Called when an actor leaves the region"""
		self._remove_actor(actor)

	def spawn_actor(self, actor, dest):
		"""Called when a new actor has been created in the region."""
		self._add_actor(actor, dest)

	def move_actor(self, actor, previous, dest):
		"""Called when an actor moves to a new location in the region."""
		self._remove_actor(actor)
		self._add_actor(actor, dest)


class InvalidRegion(KeyError):
	"""The region requested does not exist."""

class InvalidActor(KeyError):
	"""The actor requested does not exist."""



class World(Persistent):
	def __init__(self):
		self.regions = PersistentMapping()
		self.actors = IOBTree()
		self.players_by_name = OOBTree()

	def get_region(self, name):
		try:
			return self.regions[name]
		except KeyError:
			raise InvalidRegion("No such region '%s'" % name)

	def get_actor(self, id):
		try:
			return self.actors[id]
		except KeyError:
			raise InvalidActor("No such Actor with id '%s'" % id)

	def is_player_name_taken(self, name):
		return name.lower() in self.players_by_name

	def get_player(self, name):
		return self.players_by_name[name.lower()]

	def __getitem__(self, pos):
		return self.get_region(pos.layer)[pos.x, pos.y]

	def __setitem__(self, pos, loc):
		return self.get_region(pos.layer).set_location((pos.x, pos.y), loc)

	def _move_actor(self, actor, previous, dest):
		"""Move the actor from 'previous' to 'to'.

		You should not need to call this method directly.
		It is called automatically by assigning to actor.position.
		"""
		assert actor.id
		region = self.get_region(dest.layer)
		if previous:
			oldregion = self.get_region(previous.layer)
			if region == oldregion:
				oldregion.move_actor(actor, previous, dest)
			else:
				oldregion.actor_leave(actor)
				region.actor_enter(actor, dest)
		else:
			region.spawn_actor(actor, dest)
		actor._position = dest

	def spawn_actor(self, actor, dest):
		"""Add a new actor to the world at dest"""
		from wor.actors.player import Player
		if not hasattr(actor, 'id'):
			# register the actor in the index
			try:
				actor.id = self.actors.maxKey() + 1
			except ValueError:
				actor.id = 1
			self.actors[actor.id] = actor
			if isinstance(actor, Player):
				self.players_by_name[actor.name.lower()] = actor
		actor.position = dest	# triggers move_actor to handle spawning into a region

	def remove_actor(self, actor):
		"""Permanently remove an actor from the world"""
		from wor.actors.player import Player
		region = self.get_region(actor.layer)
		region.actor_leave(actor)
		del(self.actors[actor.id])
		if isinstance(actor, Player):
			del(self.players_by_name[actor.name])

	def create_region(self, name, title=None):
		r = Region(name, title)
		self.regions[name] = r
		r.world = self
		return r

	def get_spawnpoint(self, align):
		return Position(0, 0, 'main')

	def create_player(self, name, align):
		"""Creates a player with the name given and spawns it in the
		new player spawnpoint for the given alignment."""
		from wor.actors.player import Player, DuplicatePlayerName
		if name in self.players_by_name:
			raise DuplicatePlayerName('This player name already exists.')
		player = Player(name, align)
		spawn = self.get_spawnpoint(align)
		self.spawn_actor(player, spawn)
		return player

	def get_neighbourhood(self, pos, dist, player=None):
		"""Return a list of locations corresponding to the neighbourhood
		of 'pos', with respect to the compass of a given player."""
		locs = []
		this_ring = [pos]


		# For each of the other rings, we construct it using
		# information from the previous ring
		for distance in range(1, dist + 1):
			locs += this_ring
			prev_ring = this_ring
			this_ring = []

			# Each edge is essentially the same construction method
			for edge in range(0, 6):
				# For this edge of the current ring, we start with the
				# "straight-out" hex:
				dep = prev_ring[edge * (distance-1)]
				if dep == None:
					this_ring.append(None)
				else:
					loc = dep.local_directions[edge](dep, player)
					this_ring.append(loc)
					
				# Now do the remaining elements of the current ring
				for h in range(1, distance):
					prev_pos = edge * (distance - 1) + h - 1

					# This hex's antecedents
					a0 = prev_ring[prev_pos]
					a1 = prev_ring[(prev_pos + 1) % len(prev_ring)]

					# Check that neither antecedent was unknown
					if a0 == "unknown" or a1 == "unknown":
						this_ring.append("unknown")
						continue

					# Deal with the case if both antecedents are undefined
					if a0 == None and a1 == None:
						this_ring.append(None)
						continue

					# Deal with one or other antecedents being undefined
					if a0 == None:
						loc = a1.local_directions[edge](a1, player)
					elif a1 == None:
						loc = a0.local_directions[(edge + 1) % 6](a0, player)
					# or check that both paths to this hex yield the same
					# result
					elif (a1.local_directions[edge](a1, player)
						 != a0.local_directions[(edge + 1) % 6](a0, player)):
						this_ring.append("unknown")
						continue
					else:
						loc = a1.local_directions[edge](a1, player)

					this_ring.append(loc)
		return locs + this_ring
