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
		if html == None:
			self.html = self.make_button(caption, uid, ap, parameters)

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
		action_params = '"' + uid + '"'
		for it in parameters:
			action_params += ', "' + uid + '_' + it + '"'
			
		return ("<button onclick='post_action(%(params)s)'>"
				+ "%(caption)s (%(ap)d AP)</button>") % {
			'uid': uid,
			'caption': caption,
			'ap': ap,
			'params': action_params
			}
