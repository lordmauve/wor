##########
# A location

import copy
from Database import DB
from SerObject import SerObject
from Logger import log
import Context
import types

class Location(SerObject):
	_table = 'location'
	cache_by_id = {}
	cache_by_pos = {}

	####
	# Load the location
	@classmethod
	def load_by_pos(cls, pos, allprops=False):
		"""Load a complete location stack by position"""
		rpos = repr(pos)
		if rpos in Location.cache_by_pos:
			return Location.cache_by_pos[rpos]

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
		rpos = repr(obj.pos)
		cls.cache_by_pos[rpos] = obj

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
		super(Location, self).__init__()
		self.pos = pos
		self.overlay = 0
		self._underneath = None
		self._above = None
		#self.set_mapping() # FIXME: See note about this method
		
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
		ret = { 'type': self.ob_type() }

		auth = Context.authz_location(self)
		if auth == Context.ADMIN:
			fields = dir(self)
			# Filter out anything starting with __
			fields = filter(lambda x: x[0] != '_' or x[1] != '_', fields)
			# Filter out methods
			fields = filter(lambda x: not isinstance(getattr(self, x),
													 types.MethodType),
							fields)
		elif auth == Context.OWNER:
			fields = [ ]
		elif auth == Context.STRANGER_VISIBLE:
			fields = [ ]
		else:
			fields = [ ]

		for k in fields:
			if k in ( '_underneath', '_above', 'cache_by_id', 'cache_by_pos' ):
				continue
			
			try:
				v = getattr(self, k)
			except KeyError:
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

	def set_mapping(self):
		pos = [ self.e, self.ne, self.nw, self.w, self.sw, self.se ]

		# FIXME: flipped and rotated are *player* properties, not
		# location. This code should be w.r.t the viewing player
		# context, not the location.
		if self.flipped:
			self.r  = pos[(6+self.rotated) % 6]
			self.ur = pos[(5+self.rotated) % 6]
			self.ul = pos[(4+self.rotated) % 6]
			self.l  = pos[(3+self.rotated) % 6]
			self.ll = pos[(2+self.rotated) % 6]
			self.lr = pos[(1+self.rotated) % 6]
		else:
			self.r  = pos[(0+self.rotated) % 6]
			self.ur = pos[(1+self.rotated) % 6]
			self.ul = pos[(2+self.rotated) % 6]
			self.l  = pos[(3+self.rotated) % 6]
			self.ll = pos[(4+self.rotated) % 6]
			self.lr = pos[(5+self.rotated) % 6]

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
