from wor.actors.npc import *


class Barmaid(Seller, HumanFemaleNPC):
	taxonomy = 'human.female.Barmaid'
	short_name = 'the Barmaid'
	full_name_format = '%s, the barmaid'

	sells = [
		('drinks.Ale', 3),
		('drinks.Tequila', 2),
	]
