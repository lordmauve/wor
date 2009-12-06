from wor.actors.npc import *
from wor.actions import trading


class Barmaid(HumanFemaleNPC):
	taxonomy = 'human.female.Barmaid'
	short_name = 'the Barmaid'
	full_name_format = '%s, the barmaid'

	def external_actions(self, player):
		return [
			trading.ActionBuy(player, seller=self, item='drinks.Ale', price=3)
		]
