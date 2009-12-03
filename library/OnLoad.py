class OnLoad(object):
	""""Aspect" class to allow serialisable objects to receive
	an on_load event when their parent object is fully loaded."""
	def __init__(self, parent):
		self.on_load_parent = parent
		
	def __setstate__(self, state):
		super(OnLoad, self).__setstate__(state)
		if not hasattr(self.on_load_parent, '_on_load_objects'):
			self.on_load_parent._on_load_objects = []
		self.on_load_parent._on_load_objects.append(self)
