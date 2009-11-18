from Item import Item

class Scythe(Item):
	name = "scythe"
	# You can do a lot of damage with a scythe...
	damage = 4
	# Very hard to hit accurately with, though
	attack_skill = -20
	# Can cut not only grass but bigger stuff, too, like bamboo stands
	cut_grass = 2
