import random 
from base import Item, AggregateItem


class Ale(AggregateItem):
	name = 'a tankard of ale'
	name_plural = '%d tankards of ale'

	desc = 'a frothing tankard of nutty brown ale'
	desc_plural = '%d frothing tankards of nutty brown ale'

	group = "Drinks"


class Tequila(Item):
	name = 'a shot of tequila'

	desc = 'a shot of tequila'
	desc_worm = 'a shot of tequila - with a delicious tequila worm!'

	group = "Drinks"

	def __init__(self):
		super(Tequila, self).__init__()
		self.worm = random.randint(0, 10) == 0

	def description(self):
		if self.worm:
			return self.desc_worm
		return self.desc
