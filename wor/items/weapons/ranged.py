from base import Weapon


class Bow(Weapon):
	__abstract = True

	damage = 5
	attack_skill = -5
	dodge_skill = +2
	
	ammunition = 'weapon.ammo.Arrow'
	
	def on_hit(self, user, victim):
		self.weapon_break(user, victim)

	def on_miss(self, user, victim):
		self.weapon_break(user, victim)


class ShortBow(Bow):
	name = "short bow"
	desc = "an average yew short bow"


class Crossbow(Bow):
	ammunition = 'weapon.ammo.Bolt'
	desc = "a heavy oak crossbow"
