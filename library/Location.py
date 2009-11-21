##########
# A location

import copy
import functools
from Database import DB
from SerObject import SerObject
from Action import Action
from Cost import Cost
from Util import no_d
from Logger import log
import Context
import types

class Location(SerObject):
	_table = 'location'
	cache_by_id = {}
	cache_by_pos = {}

	move_ap = 1
	image_name = 'colin'

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
					pos.as_dict()
					)
		row = cur.fetchone()
		location = None
		while row is not None:
			# Load the overlay
			tmploc = cls._load_from_row(row, allprops)
			# Set up a doubly-linked list
			tmploc._underneath = location
			if location is not None:
				location._above = tmploc
			# Push the underlying location down
			location = tmploc
			row = cur.fetchone()

		if location is not None:
			location._above = None

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
		inds.update(self.pos.as_dict())
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
		while loc._underneath is not None:
			loc = loc._underneath
		return loc
	
	def stack_top(self):
		"""Return the top Location of the stack that this Location
		lives in."""
		loc = self
		while loc._above is not None:
			loc = loc._above
		return loc
	
	def deoverride(self):
		"""Unhook this location (overlay) from the stack, and remove
		it from the database."""
		self._underneath._above = self._above
		if self._above is not None:
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
		while loc is not None:
			yield loc
			loc = loc._above

	def stack_layers_rev(self):
		"""Generator function to iterate through the stack from the
		top down"""
		loc = self.stack_top()
		while loc is not None:
			yield loc
			loc = loc._underneath

	####
	# Property access

	# Walk down the stack in order until we hit the bottom or find the
	# property that we asked for.
	def __getattr__(self, key):
		try:
			return SerObject.__getattribute__(self, key)
		except AttributeError:
			if self._underneath is not None:
				return self._underneath.__getattr__(key)

		# This line is not reachable
		raise AttributeError, (key, self.__class__)

	def context_get(self):
		"""Return a dictionary of properties of this object, given the
		current authZ context"""
		ret = { 'type': self.ob_type(),
				'id': str(self._id) }

		auth = Context.authz_location(self)
		if Context.visible(auth):
			ret['actors'] = ','.join(( str(x) for x in self.actor_ids() ))
			ret['description'] = self.description(Context.context)

			if auth == Context.ADMIN:
				fields = Context.all_fields(self)
			elif auth == Context.OWNER:
				fields = [ 'name' ]
			elif auth == Context.STRANGER_VISIBLE:
				fields = [ 'name' ]
		else:
			fields = [ ]

		image_stack = []
		for overlay in self.stack_layers():
			image_stack = overlay.build_image_stack(image_stack)
		ret['stack'] = '.'.join(image_stack)

		for k in ( '_underneath', '_above', 'cache_by_id', 'cache_by_pos' ):
			if k in fields:
				fields.remove(k)

		ret['_underneath'] = str(self._underneath)
		ret['_above'] = str(self._above)

		return self.build_context(ret, fields)


	####
	# Basic properties
	def power(self, name):
		"""Return the value of the named power attribute"""
		return getattr(self, name, 0)

	def build_image_stack(self, image_stack):
		"""Given the stack of images to render the terrain up to but
		not including this overlay, return the image stack needed to
		render the terrain including this overlay."""
		try:
			image_stack.append(self.image_name)
		except AttributeError:
			pass
		return image_stack

	def __str__(self):
		return "[%s;%d]" % (str(self.pos), self.overlay)

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
		if who is None: who = Context.context
		start = 0
		if who.power('flipped'):
			start = 6 - start
		idx = (start + who.power('rotated')) % 6
		return self.directions[idx](self)

	def ur(self, who=None):
		"""Return the hex to the upper right of this one, according to the
		given player"""
		if who is None: who = Context.context
		start = 1
		if who.power('flipped'):
			start = 6 - start
		idx = (start + who.power('rotated')) % 6
		return self.directions[idx](self)

	def ul(self, who=None):
		"""Return the hex to the upper left of this one, according to the
		given player"""
		if who is None: who = Context.context
		start = 2
		if who.power('flipped'):
			start = 6 - start
		idx = (start + who.power('rotated')) % 6
		return self.directions[idx](self)

	def l(self, who=None):
		"""Return the hex to the left of this one, according to the
		given player"""
		if who is None: who = Context.context
		start = 3
		if who.power('flipped'):
			start = 6 - start
		idx = (start + who.power('rotated')) % 6
		return self.directions[idx](self)

	def ll(self, who=None):
		"""Return the hex to the lower left of this one, according to the
		given player"""
		if who is None: who = Context.context
		start = 4
		if who.power('flipped'):
			start = 6 - start
		idx = (start + who.power('rotated')) % 6
		return self.directions[idx](self)

	def lr(self, who=None):
		"""Return the hex to the lower right of this one, according to the
		given player"""
		if who is None: who = Context.context
		start = 5
		if who.power('flipped'):
			start = 6 - start
		idx = (start + who.power('rotated')) % 6
		return self.directions[idx](self)

	local_directions = [ r, ur, ul, l, ll, lr ]
	local_directions_name = [ 'r', 'ur', 'ul', 'l', 'll', 'lr' ]

	# Actions
	def external_actions(self, acts, player, name=None):
		"""Add to acts a list of actions that we could perform"""
		for i in range(0, 6):
			# FIXME: This is awkward -- why are both arrays needed?
			n = self.local_directions_name[i]
			if self.could_go(player, n):
				l = self.local_directions[i](self)
				uid = Action.make_id(self, "move_" + n)
				cost = self.move_cost(player, l)

				# Create the action function
				a = no_d(functools.partial(player.move_to, l.pos))
				# Create the action itself
				acts[uid] = Action(uid, player, caption="Move " + n.upper(),
								   cost=Cost(ap=cost),
								   action=a,
								   group="move")

	# Who's here?
	def actor_ids(self):
		"""Return a list of the actor IDs on this location"""
		ret = []
		
		cur = DB.cursor()
		cur.execute("SELECT id FROM actor"
					+ " WHERE x=%(x)s AND y=%(y)s AND layer=%(layer)s",
					self.pos.as_dict())
		row = cur.fetchone()
		while row is not None:
			ret.append(row[0])
			row = cur.fetchone()
			
		return ret

	def could_go(self, player, direction):
		# FIXME: Add support for edge conditions
		loc = getattr(self, direction)(self)
		if loc is None:
			return False
		return True

	def move_cost(self, player, destination):
		return self.move_ap + destination.move_ap
