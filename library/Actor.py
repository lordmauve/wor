##########
# Generic actor: covers players, NPCs, monsters

import types
import SerObject
import Util
import Context
from Logger import log
from Location import Location
from Action import Action

class Actor(SerObject.SerObject):
	# We have our own DB table and caching scheme for Actors
	_table = 'actor'
	cache_by_id = {}

	####
	# Creating a new object
	def __init__(self, name, position):
		"""Create a completely new actor"""
		super(Actor, self).__init__()
		self.name = name
		self.position = position

	def _save_indices(self):
		inds = super(Actor, self)._save_indices()
		inds['x'] = self.position.x
		inds['y'] = self.position.y
		inds['layer'] = self.position.layer
		return inds

	####
	# Basic properties of the object
	def loc(self):
		"""Return the Location (or Road for monsters) that we're stood on"""
		if not hasattr(self, '_loc'):
			self._loc = Location.load_by_pos(self.position)
		return self._loc

	def held_item(self):
		"""Return the item(s) currently held by the actor"""
		return None

	def equipment(self):
		"""Return an iterator over the equipment currently worn by the actor"""
		pass

	def power(self, name):
		"""Compute the effective power of a property"""
		# FIXME: Implement caching of power calculations here
		powr = 0

		# Start with intrinsics
		powr += Util.default(self[name])

		# Equipment held
		held = self.held_item()
		if held != None:
			powr += held.power(name)

		# Equipment worn
		#for item in self.equipment():
		#	powr += item.power(name)

		# Location
		powr += self.loc().power(name)

		return powr

	def context_get(self):
		"""Return a dictionary of properties of this object, given the
		current authZ context"""
		ret = {}

		auth = Context.authz_actor(self)
		if auth == Context.ADMIN:
			fields = Context.all_fields(self)
		elif auth == Context.OWNER:
			fields = [ 'ap', 'name', 'hp' ]
		elif auth == Context.STRANGER_VISIBLE:
			fields = [ 'name' ]
		else:
			fields = [ 'name' ]

		for k in fields:
			if k in ( 'cache_by_id' ):
				continue
			
			try:
				v = self[k]
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
	# Administration
	def message(self, message):
		"""Write a message to the actor's message log"""
		self.messages += message + "\n"
		if len(self.messages > 1024):
			self.messages = self.messages[-1024:]
		self._changed = True

	####
	# Actions infrastructure: Things the player can do to this actor
	def external_actions(self, acts, player):
		"""Create and return a hash of all possible actions the
		given player might perform on this actor"""

		# They could attack us...
		if self != player:
			uid = Action.make_id(self, "attack")
			acts[uid] = Action(
				uid, caption="Attack", ap=1, group="outsider",
				action=lambda: player.attack(self)
				)

	def perform_action(self, actid):
		"""Perform an action as requested."""
		actions = self.actions()
		actions[actid].perform()

	####
	# Items/inventory/equipment
	def has(self, itemtype, number=1):
		count = 0
