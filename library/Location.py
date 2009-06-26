##########
# A location

import copy
from Database import DB
from SerObject import SerObject
from Action import Action
from Logger import log
import Context
import types

class Location(SerObject):
	_table = 'location'
	cache_by_id = {}
	cache_by_pos = {}

	move_ap = 0

	####
	# Load the location
	@classmethod
	def load_by_pos(cls, pos, allprops=False):
		"""Load a complete location stack by position"""
		rpos = repr(pos)
		if rpos in Location.cache_by_pos:
			stack = Location.cache_by_pos[rpos]
			overlays = stack.keys()
			overlays.sort()
			return stack[overlays[-1]]

		cur = DB.cursor()
		cur.execute('SELECT id, state FROM location '
					+ 'WHERE x=%(x)s AND y=%(y)s AND layer=%(layer)s '
					+ 'ORDER BY overlay',
					{ 'x': pos.x,
					  'y': pos.y,
					  'layer': pos.layer }
					)
		row = cur.fetchone()
		location = None
		while row != None:
			# Load the overlay
			tmploc = cls._load_from_row(row, allprops)
			# Set up a doubly-linked list
			tmploc._underneath = location
			if location != None:
				location._above = tmploc
			# Push the underlying location down
			location = tmploc
			row = cur.fetchone()

		return location

	@classmethod
	def _cache_object(cls, obj):
		"""Hook to allow classes to define their own caching scheme.
		Called after an object has been loaded and cached in
		cls.cache_by_id"""
		super(Location, cls)._cache_object(obj)
		rpos = repr(obj.pos)
		stack = cls.cache_by_pos.setdefault(rpos, {})
		if obj.overlay in stack:
			# FIXME: Raise an exception here: we've just loaded a
			# duplicate object
			log.error("Trying to cache a Location overlay that already exists, at (%d, %d, %s, %d)" % (obj.pos.x, obj.pos.y, obj.pos.layer, obj.overlay))
			return
		stack[obj.overlay] = obj

	def _save_indices(self):
		inds = super(Location, self)._save_indices()
		inds['x'] = self.pos.x
		inds['y'] = self.pos.y
		inds['layer'] = self.pos.layer
		inds['overlay'] = self.overlay
		return inds

	####
	# Create a new location
	def __init__(self, pos):
		"""Create a completely new location"""
		self._underneath = None
		self._above = None
		super(Location, self).__init__()
		self.pos = pos
		self.overlay = 0
		self._cache_object(self)

	####
	# Stack management
	def stack_bottom(self):
		"""Return the bottom Location of the stack that this Location
		lives in."""
		loc = self
		while loc._underneath != None:
			loc = loc._underneath
		return loc
	
	def stack_top(self):
		"""Return the top Location of the stack that this Location
		lives in."""
		loc = self
		while loc._above != None:
			loc = loc._above
		return loc
	
	def deoverride(self):
		"""Unhook this location (overlay) from the stack, and remove
		it from the database."""
		self._underneath._above = self._above
		if self._above != None:
			self._above._underneath = self._underneath
		self._deleted = True

	def add_overlay(self, loc):
		"""Add loc to the top of the stack that this Location lives
		in."""
		stack_top = self.stack_top()
		loc.overlay = stack_top.overlay + 1
		stack_top._above = loc
		loc._underneath = stack_top
		loc._above = None

	def stack_layers(self):
		"""Generator function to iterate through the stack from the
		bottom upwards"""
		loc = self.stack_bottom()
		while loc != None:
			yield loc
			loc = loc._above

	def stack_layers_rev(self):
		"""Generator function to iterate through the stack from the
		top down"""
		loc = self.stack_top()
		while loc != None:
			yield loc
			loc = loc._underneath

	####
	# Property access

	# These reimplement the property access functions in SerObject.py,
	# by walking down the stack in order until we hit the bottom or
	# find the property that we asked for.
	def __getitem__(self, key):
		if key not in self.__dict__ and key[0] != '_':
			if not self._demand_load_property(key):
				if self._underneath != None:
					return self._underneath.__getitem__(key)
				else:
					self.__dict__[key] = None
		return self.__dict__[key]

	def __getattr__(self, key):
		if key not in self.__dict__ and key[0] != '_':
			if not self._demand_load_property(key):
				if self._underneath != None:
					return self._underneath.__getattr__(key)
				else:
					raise AttributeError, (key, self.__class__)
		return self.__dict__[key]

	def context_get(self):
		"""Return a dictionary of properties of this object, given the
		current authZ context"""
		ret = { 'type': self.ob_type(),
				'id': str(self._id) }

		auth = Context.authz_location(self)
		if auth == Context.ADMIN:
			fields = Context.all_fields(self)
			ret['actors'] = ','.join(( str(x) for x in self.actor_ids() ))
		elif auth == Context.OWNER:
			fields = [ 'name' ]
			ret['actors'] = ','.join(( str(x) for x in self.actor_ids() ))
		elif auth == Context.STRANGER_VISIBLE:
			fields = [ 'name' ]
			ret['actors'] = ','.join(( str(x) for x in self.actor_ids() ))
		else:
			fields = [ ]

		for k in fields:
			if k in ( '_underneath', '_above', 'cache_by_id', 'cache_by_pos' ):
				continue
			
			try:
				v = getattr(self, k)
			except AttributeError:
				pass
			else:
				if v != None:
					if hasattr(v, 'context_get'):
						ret[k] = v.context_get()
					else:
						ret[k] = str(v)

		return ret


	####
	# Basic properties
	def power(self, name):
		if hasattr(self, name):
			return self[name]
		
		return 0


	def e(self):
		"""Return the hex to the east of this one"""
		if hasattr(self, 'warp_e'):
			return load_by_pos(self.warp_e)
		pos = copy.copy(self.pos)
		pos.x += 1
		return self.load_by_pos(pos)

	def w(self):
		if hasattr(self, 'warp_w'):
			return load_by_pos(self.warp_w)
		pos = copy.copy(self.pos)
		pos.x -= 1
		return self.load_by_pos(pos)

	def ne(self):
		if hasattr(self, 'warp_ne'):
			return load_by_pos(self.warp_ne)
		pos = copy.copy(self.pos)
		pos.y += 1
		return self.load_by_pos(pos)

	def nw(self):
		if hasattr(self, 'warp_nw'):
			return load_by_pos(self.warp_nw)
		pos = copy.copy(self.pos)
		pos.x -= 1
		pos.y += 1
		return self.load_by_pos(pos)

	def se(self):
		if hasattr(self, 'warp_se'):
			return load_by_pos(self.warp_se)
		pos = copy.copy(self.pos)
		pos.x += 1
		pos.y -= 1
		return self.load_by_pos(pos)

	def sw(self):
		if hasattr(self, 'warp_sw'):
			return load_by_pos(self.warp_se)
		pos = copy.copy(self.pos)
		pos.y -= 1
		return self.load_by_pos(pos)

	"""Table used for obtaining directions algorithmically"""
	directions = [ e, ne, nw, w, sw, se ]


	def r(self, who=None):
		"""Return the hex to the right of this one, according to the
		given player"""
		if who == None: who = Context.context
		if who.power('flipped'):
			return self.directions[(6+who.power('rotated')) % 6](self)
		else:
			return self.directions[(0+who.power('rotated')) % 6](self)

	def ur(self, who=None):
		"""Return the hex to the upper right of this one, according to the
		given player"""
		if who == None: who = Context.context
		if who.power('flipped'):
			return self.directions[(5+who.power('rotated')) % 6](self)
		else:
			return self.directions[(1+who.power('rotated')) % 6](self)

	def ul(self, who=None):
		"""Return the hex to the upper left of this one, according to the
		given player"""
		if who == None: who = Context.context
		if who.power('flipped'):
			return self.directions[(4+who.power('rotated')) % 6](self)
		else:
			return self.directions[(2+who.power('rotated')) % 6](self)

	def l(self, who=None):
		"""Return the hex to the left of this one, according to the
		given player"""
		if who == None: who = Context.context
		if who.power('flipped'):
			return self.directions[(3+who.power('rotated')) % 6](self)
		else:
			return self.directions[(3+who.power('rotated')) % 6](self)

	def ll(self, who=None):
		"""Return the hex to the lower left of this one, according to the
		given player"""
		if who == None: who = Context.context
		if who.power('flipped'):
			return self.directions[(2+who.power('rotated')) % 6](self)
		else:
			return self.directions[(4+who.power('rotated')) % 6](self)

	def lr(self, who=None):
		"""Return the hex to the lower right of this one, according to the
		given player"""
		if who == None: who = Context.context
		if who.power('flipped'):
			return self.directions[(1+who.power('rotated')) % 6](self)
		else:
			return self.directions[(5+who.power('rotated')) % 6](self)

	local_directions = [ r, ur, ul, l, ll, lr ]
	local_directions_name = [ 'r', 'ur', 'ul', 'l', 'll', 'lr' ]

	# Actions
	def external_actions(self, acts, player, name=None):
		"""Add to acts a list of actions that we could perform"""
		for i in range(0, 6):
			# FIXME: This is awkward -- why are both arrays needed?
			n = self.local_directions_name[i]
			l = self.local_directions[i](self)
			if self.could_go(player, n):
				uid = Action.make_id(self, "move_" + n)
				cost = self.move_cost(player, l)
				acts[uid] = Action(uid, caption="Move " + n.upper(),
								   ap=cost,
								   action=lambda d: player.move_to(self),
								   group="move")

	# Who's here?
	def actor_ids(self):
		"""Return a list of the actor IDs on this location"""
		ret = []
		
		cur = DB.cursor()
		cur.execute("SELECT id FROM actor"
					+ " WHERE x=%(x)s AND y=%(y)s AND layer=%(layer)s",
					self.pos.__dict__)
		row = cur.fetchone()
		while row != None:
			ret.append(row[0])
			row = cur.fetchone()
			
		return ret

	def could_go(self, player, direction):
		# FIXME: Add support for edge conditions
		loc = getattr(self, direction)(self)
		if loc == None:
			return False
		return True

	def move_cost(self, player, destination):
		return self.move_ap + destination.move_ap
