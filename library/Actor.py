##########
# Generic actor: covers players, NPCs, monsters

import SerObject
import Util
import Context
from Logger import log

class Actor(SerObject.SerObject):
	####
	# Creating a new object
	def __init__(self):
		"""Create a completely new actor"""
		super(Actor, self).__init__()

	def _save_indices(self):
		inds = super(Actor, self)._save_indices()
		#inds['x'] = self.position.x
		#inds['y'] = self.position.y
		#inds['layer'] = self.position.layer
		return inds

	####
	# Basic properties of the object
	def loc(self):
		"""Return the Location (or Road for monsters) that we're stood on"""
		if self._loc == None:
			self._loc = load_location(self.position)
		return self._loc

	def held_item(self):
		"""Return the item(s) currently held by the actor"""
		pass

	def equipment(self):
		"""Return an iterator over the equipment currently worn by the actor"""
		pass

	def power(self, name):
		"""Compute the effective power of a property"""
		# FIXME: Implement caching of power calculations here
		pow = 0

		# Start with intrinsics
		pow += Util.default(self[name])

		# Equipment held
		pos += self.held_item().power(name)

		# Equipment worn
		for item in self.equipment():
			pos += item.power(name)

		# Location
		pos += self.loc().power(name)

		return pow

	def context_get(self):
		"""Return a dictionary of properties of this object, given the
		current authZ context"""
		auth = Context.authz_actor(self)
		log.debug("Context authz is " + str(auth))
		if auth == Context.ADMIN:
			fields = dir(self)
		elif auth == Context.OWNER:
			fields = [ 'ap', 'name', 'hp' ]
		elif auth == Context.STRANGER_VISIBLE:
			fields = [ 'name' ]
		else:
			fields = [ 'name' ]

		log.debug(fields)

		ret = {}
		for k in fields:
			v = self[k]
			if v != None:
				if v is object and hasattr(v, 'context_get'): # FIXME: is this right?
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
	def actions(self):
		"""Create and return a hash of all possible actions this
		player might perform"""
		return {}

	def perform_action(self, actid, req):
		"""Perform an action as requested. req is a mod_python request
		object"""
		actions = self.actions()
		actions[actid].perform(req)

	####
	# Items/inventory/equipment
	def has(self, itemtype, number=1):
		count = 0
		
