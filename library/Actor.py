##########
# Generic actor: covers players, NPCs, monsters

import types
import time

from SerObject import SerObject
import Util
import Context
from Item import Item
from Logger import log
from Location import Location
from Action import Action
from Database import DB

class Actor(SerObject):
	# We have our own DB table and caching scheme for Actors
	_table = 'actor'
	cache_by_id = {}

	####
	# Creating a new object
	def __init__(self, name, position):
		"""Create a completely new actor"""
		self.name = name
		super(Actor, self).__init__()
		self.position = position

	def _save_indices(self):
		inds = super(Actor, self)._save_indices()
		inds['x'] = self.position.x
		inds['y'] = self.position.y
		inds['layer'] = self.position.layer
		return inds

	@classmethod
	def flush_cache(cls):
		cls.cache_by_id = {}

	####
	# Basic properties of the object
	def loc(self):
		"""Return the Location (or Road for monsters) that we're stood on"""
		if not hasattr(self, '_loc'):
			self._loc = Location.load_by_pos(self.position)
		return self._loc

	def held_item(self):
		"""Return the item(s) currently held by the actor"""
		if self['holding'] == None:
			return None
		return Item.load(self.holding)

	def change_item_action(self, data):
		if 'id' not in data:
			return False
		
		try:
			self.holding = int(data['id'])
		except Exception, e:
			return False

		return True

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
		ret['id'] = str(self._id)

		auth = Context.authz_actor(self)
		if auth == Context.ADMIN:
			fields = Context.all_fields(self)
		elif auth == Context.OWNER:
			fields = [ 'ap', 'name', 'hp', 'holding' ]
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
				if v != None and k not in ret:
					if hasattr(v, 'context_get'):
						ret[k] = v.context_get()
					else:
						ret[k] = str(v)

		return ret

	####
	# Administration
	def message(self, message, msg_type='message'):
		"""Write a message to the actor's message log"""
		cur = DB.cursor()
		cur.execute("INSERT INTO actor_message"
					+ " (stamp, actor_id, msg_type, message)"
					+ " VALUES (%(stamp)s, %(id)s, %(msg_type)s, %(message)s)",
					{ 'stamp': time.time(),
					  'id': self._id,
					  'msg_type': msg_type,
					  'message': message })

	def get_messages(self, since):
		"""Get messages from this actor's message log"""
		cur = DB.cursor()
		cur.execute("SELECT stamp, msg_type, message"
					+ " FROM actor_message"
					+ " WHERE stamp >= %(since)s"
					+ "   AND actor_id = %(id)s"
					+ " ORDER BY stamp DESC"
					+ " LIMIT %(limit)s",
					{ 'since': since,
					  'id': self._id,
					  'limit': 1024 })

		result = []
		row = cur.fetchone()
		while row != None:
			result.append(row)
			row = cur.fetchone()
		return result

	####
	# Actions infrastructure: Things the player can do to this actor
	def external_actions(self, acts, player, name=None):
		"""Create and return a hash of all possible actions the
		given player might perform on this actor"""

		if name == None:
			requested = [ "attack" ]
		else:
			requested = [ name ]

		# They could attack us...
		if ("attack" in requested
			and self != player):
			
			uid = Action.make_id(self, "attack")
			acts[uid] = Action(
				uid, caption="Attack", ap=1, group="outsider",
				action=lambda: player.attack(self)
				)

	####
	# Items/inventory/equipment
	def has(self, itemtype, number=1):
		count = 0
		# FIXME: This is incomplete
		return True

	def has_item(self, item):
		# FIXME: This is incomplete
		return True
