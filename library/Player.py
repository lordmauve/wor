# coding: utf-8
########
# Player Character

import time

from Database import DB
from Actor import Actor
from Location import Location
from ItemContainer import ItemContainer

from Items.Punch import Punch

from Action import Action
from Cost import Cost
from SimpleTimedCounter import SimpleTimedCounter
from Position import Position

from Logger import log
import Util
import Context

class Player(Actor):
	# Additional caching over and above the cache by ID for actors
	cache_by_name = {}

	####
	# Load an instance of this object
	@classmethod
	def load_by_name(cls, name, allprops=False):
		"""Additional function to load a player by name instead of by
		ID"""
		if name in cls.cache_by_name:
			return cls.cache_by_name[name]

		cur = DB.cursor()
		cur.execute("SELECT id FROM " + cls._table
					+ " WHERE name = %(name)s",
					{ 'name': name } )
		row = cur.fetchone()
		if row == None:
			return None
		#log.debug("Loading player %s (=%d)" % (name, row[0]))
		return cls.load(row[0], allprops)

	@classmethod
	def _cache_object(cls, obj):
		"""Hook to allow classes to define their own caching scheme.
		Called after an object has been loaded and cached in
		cls.cache_by_id"""
		super(Player, cls)._cache_object(obj)
		# FIXME: Complain if we have a duplicate cache key
		cls.cache_by_name[obj.name] = obj

	@classmethod
	def flush_cache(cls):
		super(Player, cls).flush_cache()
		cache_by_name = {}
		
	####
	# Additional indices to write to the database on save
	def _save_indices(self):
		inds = super(Player, self)._save_indices()
		inds['name'] = self.name
		return inds

	####
	# Create a new player
	def __init__(self, name, align, position=None):
		if position == None:
			# FIXME: Make this alignment-dependent
			position = Position(0, 0, 'main')

		super(Player, self).__init__(name, position)
		self._cache_object(self)
		self.align = align
		# Start at 120AP, get one more every 6 minutes (240 per day),
		# maximum 240.
		self.ap_counter = SimpleTimedCounter(self, 120, 360, 240)
		self.hp = 300
		self.maxhp = 300
		self.inventory = ItemContainer(self, "inventory")
		punch = Punch()
		self.inventory.add(punch)

	def context_get(self):
		ret = super(Player, self).context_get()
		auth = Context.authz_actor(self)
		fields = [ 'is_zombie' ]

		return self.build_context(ret, fields)

	####
	# AP handling

	# Python 2.6:
	# @property
	def __ap_getter(self):
		"""Action points"""
		return self.ap_counter.value

	# Python 2.6:
	# @ap.setter
	def __ap_setter(self, value):
		self.ap_counter.value = value

	ap = property(__ap_getter, __ap_setter)

	####
	# Movement
	def move_to(self, pos):
		if isinstance(pos, Location):
			log.warn("move_to() passed a Location, not a Position")
			pos = pos.pos
		self.position = pos

	def teleport_to(self, pos):
		if isinstance(pos, Location):
			log.warn("teleport_to() passed a Location, not a Position")
			pos = pos.pos
		self.position = pos

	####
	# Actions
	def get_actions(self, fuid=None):
		"""Create and return a hash of all possible actions this
		player might perform"""
		acts = {}
		if self.ap <= 0:
			# No actions are possible at negative AP
			return acts
		
		if fuid == None:
			action_id = None
			name = None
		else:
			action_id = fuid.split('.')
			action_id[1] = int(action_id[1])
			name = action_id[2]
		
		# What can we do of ourselves?
		# We could say "Boo!" (debug action)
		# FIXME: Remove this
		if Util.match_id(action_id, self, "sayboo"):
			uid = Action.make_id(self, "sayboo")
			acts[uid] = Action(uid, self, caption="Say Boo",
							   action=lambda d: self.say_boo(),
							   group="player")

		# We can change the held item.
		if Util.match_id(action_id, self, "changeitem"):
			uid = Action.make_id(self, "changeitem")
			act_html = "Use item <input id='%s_id' size='3' />. " % uid
			acts[uid] = Action(
				uid, self, caption="Change", cost=Cost(ap=0),
				group="inventory",
				action=lambda d: self.change_item_action(d),
				html=act_html, parameters=['id']
				)
			acts[uid].html += acts[uid].make_button_for()

		# What can we do to the item we're holding?
		item = self.held_item()
		# Match any action at this stage
		if item != None and Util.match_id(action_id, item):
			item.external_actions(acts, self, name)
		
		# What can we do to the items we're wearing?
		# FIXME: Fill in here
		
		# What can we do to the current location?
		loc = self.loc()
		if Util.match_id(action_id, loc):
			loc.external_actions(acts, self, name)
		
		# What can we do to actors here?
		for actid in self.loc().actor_ids():
			actor = Actor.load(actid)
			if Util.match_id(action_id, actor):
				actor.external_actions(acts, self, name)

		# What can we do to actors nearby?
		# FIXME: Fill in here
		
		return acts

	def perform_action(self, action_id, data):
		"""Despatch an action to the target object. The action_id is a
		full one."""
		actions = self.get_actions(action_id)
		if action_id in actions:
			self.last_action = Context.request_time
			actions[action_id].perform(data)

	def say_boo(self):
		"""Test action"""
		if self.is_zombie():
			self.message("braaaiiinnnnssss...", "sound")
		else:
			self.message("You say 'Boo!'")
			self.message(self.name + ": Boo!", "sound")
		self.ap -= 1

	####
	# Event handlers
	def dead(self):
		"""Not so much an afterlife, more a kind of après vie."""
		# Players become zombies for a couple of minutes, go
		# "mrrrrrrgh!", and then get taken to the necropolis by the
		# necropolice.
		self.message("You have died. Have fun as a zombie, until the Necropolice come to take you away.", "zombie")
		self.message("braaiinnnssss...", "zombie")
		self.zombie_until = time.time() + 60 * 2
		self._zombie_trigger = OnLoadZombieTest(self, '_zombie_trigger')

	def is_zombie(self):
		"""Are we the walking dead?"""
		z = getattr(self, 'zombie_until', 0)
		return time.time() < z
