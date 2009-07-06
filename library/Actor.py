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

	# Define constants for scaling the to-hit function
	TO_HIT_SCALAR = 100
	TO_HIT_MIN = 0.05
	TO_HIT_MAX = 0.95

	####
	# Creating a new object
	def __init__(self, name, position):
		"""Create a completely new actor"""
		super(Actor, self).__init__()
		self.name = name
		self.position = position
		self.hp = 1

		# When HP passes zero, going down, call the dead() function
		hp_trigger = TriggerLatchDown(self, 'hp', lambda: self.dead())

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
		if getattr(self, 'holding', None) == None:
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
		powr += getattr(self, name, 0)

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

		if 'cache_by_id' in fields:
			fields.delete('cache_by_id')

		return self.build_context(ret, fields)

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
			and self._id is not player._id
			and self.is_combative(player)):
			
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

	def take_items(self, name, count=1):
		"""Remove items by name from the default item container for
		this actor"""
		log.debug(str(self._id) + ": Removing " + str(count) + " " + name)
		# FIXME: This is incomplete
		pass

	def add_items(self, name, count=1):
		"""Add items by name to the default item container for this
		actor"""
		log.debug(str(self._id) + ": Adding " + str(count) + " " + name)
		# FIXME: This is incomplete
		pass

	def add_item(self, item):
		"""Add an item to the default item container"""
		# FIXME: This is incomplete
		pass

	####
	# Luckiness
	def luck_coefficient(self):
		luck_factor = self.power('luck')
		if luck_factor < 0:
			return 100.0/(100.0-luck_factor)
		else:
			return 1.0 + luck_factor / 100.0

	def lucky(self, q):
		return random() < math.pow(q, self.luck_coefficient())

	def unlucky(self, q):
		return random() < math.pow(q, 1.0/self.luck_coefficient())

	####
	# Combat
	def is_combative(self, attacker, first_strike=True):
		"""State whether this actor is willing to engage in combat
		with the attacker"""
		# Everything is hostile by default
		# FIXME: This isn't true. :)
		return True

	def to_hit(self, victim, weapon):
		"""The to-hit percentage for us to hit the victim with the
		weapon (in the Drawing Room, with the Lead Pipe)"""
		# Work out the relative skills of the attacker and victim
		x = self.power("attack_skill") + victim.power("defend_skill")
		# Compute the core function
		f = x * math.sqrt(x*x - TO_HIT_SCALE * TO_HIT_SCALE)
		# Shift the function up, and scale so that its range is the
		# open interval (0, 1)
		f += 1.0
		f /= 2.0
		# Work out how to scale it to lie between the limits we set...
		scale = self.TO_HIT_MAX - self.TO_HIT_MIN
		# ... and do so
		return TO_HIT_MIN + scale * f

	def modify_attack_damage(self, dam, victim, weapon):
		"""Alter the damage done by us with the given weapon to the
		given victim"""
		# Put alignment bonuses to damage in here
		# Also damage multiplier, etc.
		return dam

	def modify_damage(self, dam, attacker, weapon):
		"""Alter the damage done by the given attacker with the given
		weapon"""
		# Put armour benefits in here
		return dam

	def take_damage(self, dam, weapon):
		"""Actually take damage, from the given weapon. Return True if
		we died."""
		# Put insta-kill effects in here
		self.hp -= dam
		return self.hp <= 0

	def attacked(self, attacker, weapon):
		"""We're under attack! AWOOOGA! This is the opportunity to
		riposte -- e.g. if you're a monster."""
		pass
	
	def attack(self, victim, first_strike=True):
		"""The core of the combat system. See
		http://worldofrodney.org/index.php/Dev:CombatModel"""

		if not victim.is_combative(self, first_strike):
			return False

		# FIXME: Spend the AP

		weapon = self.held_item()
		weapon.pre_attack(victim)
		
		tohit = self.to_hit(victim, weapon)
		dead = False
		broken = False
		if self.lucky(tohit):
			# We hit
			# Work out the damage
			damage = weapon.base_damage_to(victim)
			damage = self.modify_attack_damage(damage, victim, weapon)
			damage = victim.modify_damage(damage, self, weapon)
			# Do the damage
			dead = victim.take_damage(damage, self, weapon)
			# Check whether the weapon has broken
			broken = weapon.weapon_break(self, victim)
		else:
			# We missed
			weapon.miss_actor(self, victim)

		# Has the victim died?
		if not (dead or victim.hp <= 0):
			if first_strike:
				# Give them an opportunity to riposte
				victim.attacked(self, weapon)

	####
	# Events

	def dead(self):
		"""We died. What happens?"""
		pass
