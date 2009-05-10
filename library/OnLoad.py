##########
# "Aspect" class to provide infrastructure for members of SerObjects
# that want to be called on load events.

class OnLoad(object):
	def __init__(self, parent):
		self.on_load_parent = parent
		
	def __setstate__(self, state):
		for k, v in state.iteritems():
			self.__dict__[k] = v
		if 'on_load_parent' in self.__dict__:
			if '_on_load_objects' not in self.on_load_parent.__dict__:
				self.on_load_parent._on_load_objects = []
			self.on_load_parent._on_load_objects.append(self)
