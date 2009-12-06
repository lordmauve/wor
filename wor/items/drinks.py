from base import Item, AggregateItem


class Ale(AggregateItem):
	name = 'a tankard of ale'
	name_plural = '%d tankards of ale'

	desc = 'a frothing tankard of nutty brown ale'
	desc_plural = '%d frothing tankards of nutty brown ale'

	group = "Drinks"
