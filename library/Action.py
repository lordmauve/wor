######
# An action: something that the user can be invited to do

class Action(object):
	def __init__(self, uid, caption="Use", ap=1,
				 action=lambda d: None,
				 group="none", html=None, parameters=[]):
		self.uid = uid
		self.caption = caption
		self.ap = ap
		self.action = action
		self.group = group
		self.parameters = parameters
		self.html = html
		if html == None:
			self.html = self.make_button_for()

	def context_get(self):
		ret = {}
		ret['html'] = self.html
		ret['ap'] = self.ap
		ret['uid'] = self.uid
		ret['caption'] = self.caption
		ret['group'] = self.group
		ret['parameters'] = ' '.join((self.uid + "_" + x for x in self.parameters))

		return ret

	def perform(self, data):
		return self.action(data)

	@staticmethod
	def make_id(object, act):
		return "%s.%d.%s" % (object.ob_type(), object._id, act)

	@staticmethod
	def make_button(caption, uid, ap=1, parameters=[]):
		"""Make a button, with appropriate caption and JavaScript to
		despatch the request."""
		action_params = '"' + uid + '"'
		for it in parameters:
			action_params += ', "' + uid + '_' + it + '"'
		aptext = ""
		if ap == 0:
			aptext = " (%d AP)" % ap
			
		return ("<button onclick='post_action(%(params)s)'>"
				+ "%(caption)s%(aptext)s</button>") % {
			'uid': uid,
			'caption': caption,
			'aptext': aptext,
			'params': action_params
			}

	def make_button_for(self, caption=None, ap=None, parameters=None):
		"""Make a button for this Action object."""
		if caption == None:
			caption = self.caption
		if ap == None:
			ap = self.ap
		if parameters == None:
			parameters = self.parameters
		return self.make_button(caption, self.uid, ap, parameters)
