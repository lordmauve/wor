####
# Trigger handling: The watched value dropped below some threshold

from Trigger import Trigger

class TriggerLatchDown(Trigger):
	"""Trigger to call a function when a value passes some threshold"""
	def __init__(self, parent, sourcekey, action, threshold=0):
		super(TriggerLatchDown, self).__init__(parent, sourcekey)
		self.threshold = threshold
		self.action = action

	def change(self, key, old, new):
		# If we have passed the threshold this time, call the action
		if old > self.threshold and new <= self.threshold:
			self.action()
