######
# An action: something that the user can be invited to do

class Action(object):
	def __init__(self, uid, caption="Use", ap=1,
				 action=lambda d: None,
				 group="none", html=None):
		self.uid = uid
		self.caption = caption
		self.ap = ap
		self.action = action
		self.group = group
		if html == None:
			self.html = self.make_button(caption, uid, ap)

	def context_get(self):
		ret = {}
		ret['html'] = self.html
		ret['ap'] = self.ap
		ret['uid'] = self.uid
		ret['caption'] = self.caption
		ret['group'] = self.group

		return ret

	def perform(self, data):
		return self.action(data)

	@staticmethod
	def make_id(object, act):
		return "%s.%d.%s" % (object.ob_type(), object._id, act)

	@staticmethod
	def make_button(caption, uid, ap=1):
		return ("<button onclick='post_action(\"%(uid)s\")'>"
				+ "%(caption)s (%(ap)d AP)</button>") % {
			'uid': uid,
			'caption': caption,
			'ap': ap
			}
