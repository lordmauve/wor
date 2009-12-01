# coding: utf-8

import time

from wor.actors.actor import Actor
from wor.world.location import Location
from wor.items.container import Inventory
from wor.items.martial import Punch

from SimpleTimedCounter import SimpleTimedCounter
from Position import Position

from Alignment import Alignment
from Logger import log
import Util
from Context import Context


from wor.actions.inventory import ActionChangeItem


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

	context_fields = ['name', 'id', 'hp', 'maxhp', 'is_zombie']

	def context_extra(self, context):
		return {
			'ap': '%d/%d' % (self.ap_counter.value, self.ap_counter.maximum),
			'hp': '%d/%d' % (self.hp, self.maxhp),
			'alignment': Alignment(self.align).name()
		}

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

	def get_actions(self):
		"""Create and return a hash of all possible actions this player might perform.

		"""
		# No actions are possible at negative AP
		if self.ap <= 0:
			return {}

		actions = [
			ActionChangeItem(self) # We can change the held item
		]

		# What can we do to the item we're holding?
		item = self.held_item()
		if item:
			actions += item.external_actions(self)
		
		# What can we do to the items we're wearing?
		# FIXME: Fill in here
		
		# What can we do to the current location?
		loc = self.loc()
		if loc:
			actions += loc.external_actions(self)
		
		# What can we do to actors here?
		for actor in self.loc().actors():
			actions += actor.external_actions(self)

		# What can we do to actors nearby?
		# FIXME: Fill in here
		
		return actions

	def perform_action(self, action_id, data):
		"""Despatch an action to the target object. The action_id is a
		full one."""
		actions = self.get_actions()
		for a in actions:
			if a.get_uid() != action_id:
				continue
			a.perform(data)
			self.last_action = time.time()
			return
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
