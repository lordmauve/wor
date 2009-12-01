# coding: utf-8

import time

from wor.actors.actor import Actor
from wor.world.location import Location
from wor.items.container import Inventory
from wor.items.martial import Punch

from Action import Action
from Cost import Cost
from SimpleTimedCounter import SimpleTimedCounter
from Position import Position

from Logger import log
import Util
from Context import Context


class ActionChangeItem(Action):
	def action(self, data):
		self.actor.change_item_action(data)


class DuplicatePlayerName(Exception):
	"""The player name requested already exists."""


class Player(Actor):
	@classmethod
	def load_by_name(cls, name):
		"""Additional function to load a player by name instead of by
		ID"""
		from wor.db import db
		return db.world().get_player(name)

	def __init__(self, name, align):
		super(Player, self).__init__(name)
		self.align = align
		# Start at 120AP, get one more every 6 minutes (240 per day),
		# maximum 240.
		self.ap_counter = SimpleTimedCounter(self, 120, 360, 240)
		self.hp = 300
		self.maxhp = 300
		self.inventory = Inventory(self)
		self.inventory.create('martial.Punch')

	def get_context(self):
		return Context(self)

	context_fields = ['name', 'id', 'hp', 'maxhp', 'position', 'align', 'is_zombie', 'ap_counter']

	def context_get(self, context):
		ret = super(Player, self).context_get(context)
		auth = context.authz_actor(self)
#		fields = ['is_zombie']

		return ret

	def __ap_getter(self):
		"""Action points"""
		return self.ap_counter.value

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
		
		if fuid is None:
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
			acts[uid] = ActionChangeItem(
				uid, self,
				caption="Change",
				cost=Cost(),
				group="inventory",
				action=lambda d: self.change_item_action(d),
				parameters=['id']
			)

		# What can we do to the item we're holding?
		item = self.held_item()
		# Match any action at this stage
		if item is not None and Util.match_id(action_id, item):
			item.external_actions(acts, self, name)
		
		# What can we do to the items we're wearing?
		# FIXME: Fill in here
		
		# What can we do to the current location?
		loc = self.loc()
		if Util.match_id(action_id, loc):
			loc.external_actions(acts, self, name)
		
		# What can we do to actors here?
		for actor in self.loc().actors():
			if Util.match_id(action_id, actor):
				actor.external_actions(acts, self, name)

		# What can we do to actors nearby?
		# FIXME: Fill in here
		
		return acts

	def perform_action(self, action_id, data):
		"""Despatch an action to the target object. The action_id is a
		full one."""
		actions = self.get_actions()
		if action_id in actions:
			self.last_action = time.time()
			actions[action_id].perform(data)
		else:
			raise KeyError("Unknown action")

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
