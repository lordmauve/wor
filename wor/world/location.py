import functools

from persistent import Persistent

from Cost import Cost
from Util import no_d
from Logger import log
import Context
import types

from wor.jsonutil import JSONSerialisable
from wor.actions.movement import ActionMove


class NullLocation(object):
	title = ''
	description = ''
	id = None
	move_ap = 1

	def no(self, who):
		return NullLocation(self.pos)

	local_directions = [no] * 6 

	def __init__(self, pos):
		self.pos = pos

	def get_title(self):
		return None

	def context_get(self, context=None):
		return None

	def can_enter(self, actor):
		return False


class Location(Persistent, JSONSerialisable):
	move_ap = 1

	pos = None
	region = None

	def __init__(self, title=None, description=''):
		self.title = title
		self.description = ''

	def get_title(self):
		return self.title or self.__class__.__name__

	@classmethod
	def class_name(cls):
		return cls.__name__

	@property
	def id(self):	
		return str(self.pos)

	@classmethod
	def load_by_pos(cls, pos):
		"""Load a complete location stack by position"""
		from wor.db import db
		try:
			return db.world()[pos]
		except KeyError:
			return NullLocation(pos)

	@classmethod
	def internal_name(cls):
		return cls.__module__.replace('wor.locations.', '') + '.' + cls.__name__

	@classmethod
	def get_class(cls, name):
		"""Obtain and cache an item class object by name"""
		locs = Location.list_all_classes()
		return locs[name]

	@classmethod
	def list_all_classes(cls):
		"""Obtain a list of all Location class names"""
		from wor import locations
		try:
			return cls._loc_cache
		except AttributeError:
			loc_map = {}
			for k, v in locations.__dict__.items():
				if (isinstance(v, type)
					and issubclass(v, Location)
					and v is not Location):
					loc_map[v.internal_name()] = v
			cls._loc_cache = loc_map
			return loc_map

	context_fields = ['pos', 'actors', 'description', 'class_name']

	def context_extra(self, context):
		return {
			'title': self.get_title(),
			'timeofday': self.region.get_time_of_day()
		}

	def context_authz(self, context):
		auth = context.authz_location(self)
		if auth == Context.ADMIN:
			return

		if context.visible(auth):
			return ['title', 'actors', 'class_name', 'description', 'timeofday']
		return []

	def power(self, name):
		"""Return the value of the named power attribute"""
		return getattr(self, name, 0)

	def __str__(self):
		return "Location(%r)" % self.pos

	def e(self):
		"""Return the hex to the east of this one"""
		if hasattr(self, 'warp_e'):
			return self.load_by_pos(self.warp_e)
		return self.load_by_pos(self.pos.translate(1, 0))

	def w(self):
		"""Return the hex to the west of this one"""
		if hasattr(self, 'warp_w'):
			return self.load_by_pos(self.warp_w)
		return self.load_by_pos(self.pos.translate(-1, 0))

	def ne(self):
		"""Return the hex to the north-east of this one"""
		if hasattr(self, 'warp_ne'):
			return self.load_by_pos(self.warp_ne)
		return self.load_by_pos(self.pos.translate(0, 1))

	def nw(self):
		"""Return the hex to the north-west of this one"""
		if hasattr(self, 'warp_nw'):
			return self.load_by_pos(self.warp_nw)
		return self.load_by_pos(self.pos.translate(-1, 1))

	def se(self):
		"""Return the hex to the south-east of this one"""
		if hasattr(self, 'warp_se'):
			return self.load_by_pos(self.warp_se)
		return self.load_by_pos(self.pos.translate(1, -1))

	def sw(self):
		"""Return the hex to the south-west of this one"""
		if hasattr(self, 'warp_sw'):
			return self.load_by_pos(self.warp_se)
		return self.load_by_pos(self.pos.translate(0, -1))


	"""Table used for obtaining directions algorithmically"""
	directions = [ e, ne, nw, w, sw, se ]


	def r(self, who=None):
		"""Return the hex to the right of this one, according to the
		given player"""
		if who is None: return self.e()
		start = 0
		if who.power('flipped'):
			start = 6 - start
		idx = (start + who.power('rotated')) % 6
		return self.directions[idx](self)

	def ur(self, who=None):
		"""Return the hex to the upper right of this one, according to the
		given player"""
		if who is None: return self.ne()
		start = 1
		if who.power('flipped'):
			start = 6 - start
		idx = (start + who.power('rotated')) % 6
		return self.directions[idx](self)

	def ul(self, who=None):
		"""Return the hex to the upper left of this one, according to the
		given player"""
		if who is None: return self.nw()
		start = 2
		if who.power('flipped'):
			start = 6 - start
		idx = (start + who.power('rotated')) % 6
		return self.directions[idx](self)

	def l(self, who=None):
		"""Return the hex to the left of this one, according to the
		given player"""
		if who is None: return self.w()
		start = 3
		if who.power('flipped'):
			start = 6 - start
		idx = (start + who.power('rotated')) % 6
		return self.directions[idx](self)

	def ll(self, who=None):
		"""Return the hex to the lower left of this one, according to the
		given player"""
		if who is None: return self.sw()
		start = 4
		if who.power('flipped'):
			start = 6 - start
		idx = (start + who.power('rotated')) % 6
		return self.directions[idx](self)

	def lr(self, who=None):
		"""Return the hex to the lower right of this one, according to the
		given player"""
		if who is None: return self.se()
		start = 5
		if who.power('flipped'):
			start = 6 - start
		idx = (start + who.power('rotated')) % 6
		return self.directions[idx](self)

	local_directions = [ r, ur, ul, l, ll, lr ]
	local_directions_name = [ 'r', 'ur', 'ul', 'l', 'll', 'lr' ]

	# Actions
	def external_actions(self, player):
		"""Add to acts a list of actions that we could perform"""

		actions = []
		for i in range(0, 6):
			# FIXME: This is awkward -- why are both arrays needed?
			n = self.local_directions_name[i]
			if self.could_go(player, n):
				l = self.local_directions[i](self)
				cost = self.move_cost(player, l)

				# Create the action function
				a = no_d(functools.partial(player.move_to, l.pos))
				# Create the action itself
				actions.append(ActionMove(player, n.upper(), cost=Cost(ap=cost)))
		return actions

	# Who's here?
	def actors(self):
		"""Return a list of the actors on this location"""
		return self.region.get_actors_at(self.pos)

	def could_go(self, player, direction):
		# FIXME: Add support for edge conditions
		loc = getattr(self, direction)(self)
		if loc is None:
			return False
		return loc.can_enter(player)

	def can_enter(self, actor):
		return True

	def move_cost(self, player, destination):
		return self.move_ap + destination.move_ap

