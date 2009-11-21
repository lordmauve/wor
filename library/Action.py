######
# An action: something that the user can be invited to do

from Cost import Cost

FAIL = -1

class Action(object):
	def __init__(self, uid, actor, caption="Use", cost=Cost(ap=1),
				 action=lambda d: None,
				 group="none", html=None, parameters=[]):
		self.uid = uid
		self.actor = actor
		self.caption = caption
		self.cost = cost
		self.action = action
		self.group = group
		self.parameters = parameters
		self.html = html
		if html is None:
			self.html = self.make_button_for()

	def context_get(self):
		ret = {}
		ret['html'] = self.html
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

	@staticmethod
	def make_id(object, act):
		return "%s.%d.%s" % (object.ob_type(), object._id, act)

	@staticmethod
	def make_button(caption, uid, cost=Cost(), parameters=[]):
		"""Make a button, with appropriate caption and JavaScript to
		despatch the request."""
		action_params = '"' + uid + '"'
		for it in parameters:
			action_params += ', "' + uid + '_' + it + '"'
		aptext = ""
		cost = str(cost)
		if cost:
			aptext = " (%s)" % cost
			
		return ("<button onclick='post_action(%(params)s)'>"
				+ "%(caption)s%(aptext)s</button>") % {
			'uid': uid,
			'caption': caption,
			'aptext': aptext,
			'params': action_params
			}

	def make_button_for(self, caption=None, cost=None, parameters=None):
		"""Make a button for this Action object."""
		if caption is None:
			caption = self.caption
		if cost is None:
			cost = self.cost
		if parameters is None:
			parameters = self.parameters
		return self.make_button(caption, self.uid, cost, parameters)
