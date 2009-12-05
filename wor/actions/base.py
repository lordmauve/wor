from Cost import Cost


class ValidationError(Exception):
	"""The action parameters did not validate."""


class SayField(object):
	"""An input field corresponding to a 'say' message box"""
	def __init__(self, name, default=''):
		self.name = name
		self.default = ''

	def clean(self, value):
		v = value.strip()
		if not v:
			raise ValidationError("You must enter a message.")
		return v

	def context_get(self):
		return {
			'name': self.name,
			'type': self.__class__.__name__,
			'default': self.default,
		}


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
		if self.cost:
			ret['cost'] = str(self.cost)
		ret['uid'] = self.get_uid()
		ret['caption'] = self.get_caption()
		ret['group'] = self.group

		params = self.get_parameters()
		if params:
			ps = []
			for p in params:
				if isinstance(p, str) or isinstance(p, unicode):
					ps.append(p)
				else:
					ps.append(p.context_get())
			ret['parameters'] = ps

		return ret

	def get_kwargs(self, data):
		kw = {}
		params = self.get_parameters()
		if not params:
			return {}
		for p in params:
			if isinstance(p, str) or isinstance(p, unicode):
				continue
			val = p.clean(data.get(p.name, ''))
			kw[p.name] = val
		return kw	

	def perform(self, data):
		kwargs = self.get_kwargs(data)
		message = self.action(**kwargs)
		if self.cost:
			self.cost.charge(self.actor)
		return message

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
