####
# ActionMake: Subclass of an Action object for making stuff

from Action import Action
from Logger import log

class ActionMake(Action):
	def __init__(self, player, item, plan):
		uid = Action.make_id(item, plan.name)
		super(ActionMake, self).__init__(
			uid, caption="Make",
			ap=plan.ap, group="build"
			)
		
		self.action = lambda d: self.build(d)
		self.item = item

		self.parameters = ['quantity']

		# What are we making?
		self.html = "Make "
		self.html += self.objectlist(player, plan.makes)

		# What are we making it from?
		self.html += " from "
		self.html += self.objectlist(player, plan.materials)

		self.html += " <input id='%s_quantity' size='3'> times. " % self.uid
		self.html += self.make_button(self.caption, self.uid,
									  self.ap, self.parameters)

	def build(self, data):
		plan.make(self.player, data[self.uid + 'quantity'])

	def objectlist(self, player, hash):
		"""Return a well-formatted string describing the set of items
		passed in hash"""
		ret = ""
		bits = []
		for item, quant in hash.iteritems():
			# item.get_class() is a @classmethod, but we use the
			# object "item" here to reference it in order to get
			# around the problem of circular references, as Item
			# imports ActionMake, so we can't import Item in this
			# module.
			icls = self.item.get_class(item)
			bits.append(str(quant) + " " + icls.name_for(player, quant))

		ret += ', '.join(bits[:-1])
		if len(bits) > 1:
			ret += " and "
		if len(bits) > 0:
			ret += bits[-1]
		return ret