##########
# Test for a single event on load, call a method, and then remove this
# listener. Subclasses of this class should implement event() and
# action() methods

class OnLoadOneShot(OnLoad):
	def __init__(self, parent, name):
		super(OnLoadOneShot, self).__init__(parent)
		self.name = name

	def on_load(self):
		# Check that the event in question has happened
		if self.event():
			# Remove ourselves from the parent
			delattr(self.on_load_parent, self.name)
			# Do what we were asked to do
			self.action()

	def event(self):
		"""Use your own implementation of this method"""
		return True

	def action(self):
		"""Use your own implementation of this method"""
		pass
