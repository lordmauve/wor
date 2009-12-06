from wor.actors.npc import *


class Barmaid(HumanFemaleNPC):
	taxonomy = 'human.female.Barmaid'
	short_name = 'the Barmaid'
	full_name_format = '%s, the barmaid'

	def external_actions(self, player):
		return []
