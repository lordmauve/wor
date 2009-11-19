from Trigger import Trigger

class TriggerDeath(Trigger):
	"""Trigger to call the dead() function on an actor when their HP
	drops below the threshold"""
	def __init__(self, parent):
		super(TriggerDeath, self).__init__(parent, 'hp')

	def change(self, key, old, new):
		# If we have passed the threshold this time, call the action
		if old > 0 and new <= 0:
			self.parent.dead()
