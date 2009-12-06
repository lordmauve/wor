import random
import os.path

from BaseConfig import base_dir

from wor.actors.mob import Mob
from wor.actions import trading

def random_name_from_file(filename):
	"""This opens the file and passes it twice to select a line
	at random. Obviously this is inefficient; as an optimisation
	we could index the file, or simply extract a bunch of names.

	"""
	f = open(os.path.join(base_dir, filename))
	num = 0
	for l in f:
		num += 1
	f.seek(0)
	which = random.randint(0, num)
	for i, l in enumerate(f):
		if i == which:
			break
	f.close()
	return l.strip()
	

class NPC(Mob):
	def __init__(self, name, behaviour):
		super(NPC, self).__init__(behaviour)
		self.name = name

	def full_name(self):
		return self.full_name_format % self.name

	context_fields = ['id', 'hp', 'class_name', 'short_name', 'full_name']

	def context_extra(self, context):
		ctx = {}
		auth = context.authz_actor(self)
		if context.visible(auth):
			ctx['actions'] = [a.context_get(context) for a in self.external_actions(context.player)]
		return ctx


class HumanFemaleNPC(NPC):
	def __init__(self, behaviour):
		given = random_name_from_file('names/female-names.txt')
		family = random_name_from_file('names/surnames.txt')

		super(HumanFemaleNPC, self).__init__(given + ' ' + family, behaviour)


class HumanMaleNPC(NPC):
	def __init__(self, behaviour):
		given = random_name_from_file('names/male-names.txt')
		family = random_name_from_file('names/surnames.txt')

		super(HumanMaleNPC, self).__init__(given + ' ' + family, behaviour)


class Seller(object):
	"""Mix-in class for NPCs that sell things.

	NPCs that want to sell things should inherit from (Seller, NPC),
	and provide an attribute 'sells', a list of tuples of the form
	
		(item_class, cost in GP)
	"""
	sells = []
	def external_actions(self, player):
		acts = []
		for item, price in self.sells:
			acts.append(trading.ActionBuy(player, seller=self, item=item, price=price))
		return acts