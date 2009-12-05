"""Generic actor: covers players, NPCs, monsters"""

import types
import time

from persistent import Persistent
from persistent.list import PersistentList
from BTrees.IOBTree import IOBTree

import Context
from Logger import log

from Triggerable import Triggerable
from TriggerDeath import TriggerDeath


from wor.actions.combat import ActionAttack
from wor.jsonutil import JSONSerialisable



class MessageLog(IOBTree):
	"""A message log for an actor.

	Messages are stored in a integer-indexed BTree for performance;
	the indices are integer timestamps.
	"""
	def message(self, message, msg_type='message', sender=None):
		"""Write a message to the actor's message log.
		"""
		t = int(time.time())
		if sender:
			msg = (t, msg_type, message, sender.name, getattr(sender, 'align', None))
		else:
			msg = (t, msg_type, message)
		self.setdefault(t, PersistentList()).append(msg)

	def get_messages(self, since):
		msgs = []
		for i in self.itervalues(int(since)):
			msgs += i
		return msgs


class Actor(Persistent, Triggerable, JSONSerialisable):
	# Define constants for scaling the to-hit function
	TO_HIT_SCALE = 100
	TO_HIT_MIN = 0.05
	TO_HIT_MAX = 0.95

	def __init__(self, name):
		"""Create a completely new actor"""
		super(Actor, self).__init__()
		self.name = name
		self._position = None
		self.hp = 1

		# When HP passes zero, going down, call the dead() function
		hp_trigger = TriggerDeath(self)

	def get_name(self):
		return self.name

	def _set_position(self, pos):
		from wor.db import db
		db.world()._move_actor(self, self._position, pos)

	def _get_position(self):
		return self._position

	position = property(_get_position, _set_position)

	def loc(self):
		"""Return the Location (or Road for monsters) that we're stood on"""
		if not hasattr(self, '_loc'):
			from wor.db import db
			self._v_loc = db.world()[self.position]
		return self._v_loc

	def held_item(self):
		"""Return the item(s) currently held by the actor"""
		return getattr(self, 'holding', None)

	def set_held_item(self, item):
		"""Set the held item"""
		self.holding = item

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
		if held is not None:
			powr += held.power(name)

		# Equipment worn
		#for item in self.equipment():
		#	powr += item.power(name)

		# Location
		powr += self.loc().power(name)

		return powr

	def context_get_(self, context):
		"""Return a dictionary of properties of this object, given the
		current authZ context"""
		ret = {}
		ret['id'] = self.id

		auth = context.authz_actor(self)
		if auth == Context.ADMIN:
			fields = Context.all_fields(self)
		elif auth == Context.OWNER:
			fields = [ 'ap', 'ap_counter', 'name', 'hp', 'maxhp', 'holding' ]
		elif auth == Context.STRANGER_VISIBLE:
			fields = [ 'name' ]
		else:
			fields = [ 'name' ]

		return self.build_context(ret, fields)

	def message(self, message, msg_type='message', sender=None):
		"""Write a message to the actor's message log, creating it
		if it does not yet exist.

		"""
		if not hasattr(self, 'messages'):
			self.messages = MessageLog()

		self.messages.message(message, msg_type, sender=sender)

	def get_messages(self, since):
		if not hasattr(self, 'messages'):
			return []

		return list(self.messages.get_messages(since))

	def external_actions(self, player):
		"""Create and return a hash of all possible actions the
		given player might perform on this actor.
		
		"""
		actions = []
		weap = player.held_item()

		# They could attack us...
		if weap and ("attack" in requested
			and self.id is not player.id
			and self.is_combative(player)):
			
			actions.append(ActionAttack(player, self))

		return actions

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

