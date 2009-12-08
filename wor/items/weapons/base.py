from wor.items.base import Item


class Weapon(Item):
	"""A weapon is an item that can be used to attack an opponent."""
	__abstract = True

	uses = 0

	victim_miss_message = "%(attacker)s takes a swing at you, narrowly missing!"
	attacker_miss_message = "You take a swing at %(victim)s but miss by an inch!"

	victim_miss_message = "%(attacker)s takes a chunk out of you!"
	attacker_miss_message = "You hit %(victim)s!"

	def pre_attack(self, victim):
		"""Called before any attack happens"""
		pass

	def base_damage_to(self, victim):
		"""Return the base damage of this weapon"""
		return self.damage

	def weapon_break(self, user, victim):
		"""Test for breakage after hitting someone.

		If the weapon breaks, remove it from the player's inventory and
		add it as a BrokenWeapon.
		"""
		self.uses += 1
		broken = user.unlucky(self.break_profile(self.uses))
		if broken:
			user.inventory.remove(self)
			broken_weapon = BrokenWeapon(self)
			user.inventory.add(broken_weapon)

			if user.held_item() is self:
				user.set_held_item(broken_weapon)
			user.message(u'Your %s has broken.' % unicode(self), 'info')

	def on_hit(self, user, victim):
		"""What to do if we hit the victim."""
		from wor.actors.player import Player
		self.weapon_break(user, victim)
		params = {
			'attacker': user.name,
			'victim': victim.name,
		}
		if isinstance(victim, Player):	# Mobs don't need messages
			victim.message(self.victim_hit_message % params, 'combat')
		user.message(self.attacker_hit_message % params, 'combat')

	def on_miss(self, user, victim):
		"""What to do if we missed the victim"""
		from wor.actors.player import Player
		params = {
			'attacker': user.name,
			'victim': victim.name,
		}
		if isinstance(victim, Player):	# Mobs don't need messages
			victim.message(self.victim_miss_message % params, 'combat')
		user.message(self.attacker_miss_message % params, 'combat')


class BrokenWeapon(Item):
	"""Wrapper for a weapon that converts it to a broken weapon."""
	__abstract = True

	def __init__(self, weapon):
		self.weapon = weapon

	def __unicode__(self):
		return u"broken " + unicode(self.weapon)

	def description(self):
		return self.weapon.broken_desc
