from Cost import Cost


class Action(object):
	"""Something that the user can be invited to do.

	This class is the abstract base class of all actions.
	"""

	group = u"Miscellaneous"
	cost = None

	def __init__(self, actor):
		self.actor = actor

	def get_caption(self):
		raise NotImplementedError("Subclasses must implement Action.get_caption")

	def get_uid(self):
		"""Return a unique ID identifying this action"""
		raise NotImplementedError("Subclasses must implement Action.get_uid")

	def get_parameters(self):
		"""Get a list of the input fields required
		to process this action."""
		return None
		
	def context_get(self, context):
		ret = {}
		ret['cost'] = str(self.cost)
		ret['uid'] = self.get_uid()
		ret['caption'] = self.get_caption()
		ret['group'] = self.group
		ret['parameters'] = self.get_parameters()

		return ret

	def perform(self, data):
		rv = self.action(data)
		if not rv:
			self.cost.charge(self.actor)
		return rv

	def action(self, data):
		pass

	@staticmethod
	def make_id(object, act):
		if hasattr(object, 'internal_name'):
			return "%s.%s.%s" % (object.internal_name(), object.id, act)
		return "%s.%s.%s" % (object.__class__.__name__, object.id, act)


class TargettedAction(Action):
	"""An action which is directed at another actor specifically.

	"""
	caption = u'Do something mysterious to %s'

	def __init__(self, actor, target):
		super(TargettedAction, self).__init__(actor)
		self.target = target

	def get_uid(self):
		mod = self.__class__.__module__
		name = self.__class__.__name__
		return '%s.%s(%d)' % (mod.lower(), name.lower(), self.target.id)

	def get_caption(self):
		return self.caption % self.target.get_name()
