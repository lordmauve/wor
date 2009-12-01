######
# An action: something that the user can be invited to do

from Cost import Cost

FAIL = -1

class Action(object):
	def __init__(self, uid, actor, caption="Use", cost=Cost(ap=1),
				 action=None,
				 group="none", parameters=[]):
		self.uid = uid
		self.actor = actor
		self.caption = caption
		self.cost = cost
		self.action_callback = action
		self.group = group
		self.parameters = parameters

	def context_get(self, context):
		ret = {}
		ret['cost'] = str(self.cost)
		ret['uid'] = self.uid
		ret['caption'] = self.caption
		ret['group'] = self.group
		ret['parameters'] = ' '.join((self.uid + "_" + x for x in self.parameters))

		return ret

	def perform(self, data):
		rv = self.action(data)
		if not rv:
			self.cost.charge(self.actor)
		return rv

	def action(self, data):
		if self.action_callback is not None:
			self.action_callback(data)

	@staticmethod
	def make_id(object, act):
		if hasattr(object, 'internal_name'):
			return "%s.%s.%s" % (object.internal_name(), object.id, act)
		return "%s.%s.%s" % (object.__class__.__name__, object.id, act)
