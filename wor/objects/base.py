from wor.jsonutil import JSONSerialisable


class WorldObject(JSONSerialisable):
	"""A WorldObject is some object too large to pick up
	but smaller than a tile. Thus pubs, shops, boats, etc
	would all count as WorldObjects"""
	
	description = ''
	_position = None
	owner = None
	
	def get_name(self):
		return getattr(self, 'name', self.__class__.__name__)

	__str__ = get_name

	def _set_position(self, pos):
		from wor.db import db
		db.world()._move_object(self, self._position, pos)

	def _get_position(self):
		return self._position

	position = property(_get_position, _set_position)

	def loc(self):
		try:
			return self._v_loc
		except AttributeError:
			from wor.db import db
			self._v_loc = db.world()[self.position]
			return self._v_loc
		
	def get_description(self):
		return self.description

	context_fields = []

	def context_extra(self, context):
		ctx = {
			'name': self.get_name(),
			'type': self.__class__.__name__,
			'description': self.get_description()
		}
		auth = context.authz_object(self)
		if context.visible(auth):
			ctx['actions'] = [a.context_get(context) for a in self.external_actions(context.player)]
		return ctx

	def external_actions(self, player):
		return []
