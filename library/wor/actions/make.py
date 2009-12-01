from base import Action
from Cost import Cost
from Logger import log


class ActionMake(Action):
	"""An action for making stuff according to a plan."""

	def __init__(self, player, item, plan):
		uid = Action.make_id(item, plan.name)
		super(ActionMake, self).__init__(
			uid, player, caption="Make",
			cost=Cost(ap=plan.ap), group="build"
			)
		
		self.item = item
		self.plan = plan
		self.player = player

		self.parameters = ['quantity']

		# What are we making?
		self.html = "Make "
		self.html += self.objectlist(self.plan.makes)

		# What are we making it from?
		self.html += " from "
		self.html += self.objectlist(self.plan.materials)

		self.html += " <input id='%s_quantity' size='3' /> times. " % self.uid
		self.html += self.make_button_for()

	def action(self, data):
		return self.plan.make(self.player, data[self.uid + '_quantity'])

	def objectlist(self, hash):
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
			bits.append(str(quant) + " " + icls.name_for(self.player, quant))

		ret += ', '.join(bits[:-1])
		if len(bits) > 1:
			ret += " and "
		if len(bits) > 0:
			ret += bits[-1]
		return ret
