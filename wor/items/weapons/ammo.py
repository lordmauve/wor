from wor.items.base import AggregateItem


class Bolt(AggregateItem):
	name = 'bolt'

	desc = 'a crossbow bolt'
	desc_plural = '%d crossbow bolts'


class Arrow(AggregateItem):
	name = 'arrow'

	desc = 'an iron-tipped, triple-fletched arrow'
	desc_plural = '%d iron-tipped, triple-fletched arrows'
