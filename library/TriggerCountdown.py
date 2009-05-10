####
# More complex trigger handling

from Trigger import Trigger

class TriggerCountdown(Trigger):
	"""Trigger to count down a parameter (by one) for every decrease
	in another."""
	def __init__(self, parent, sourcekey, targetkey, increment=-1, minimum=0):
		super(TriggerCountdown, self).__init__(parent, sourcekey)
		self.targetkey = targetkey
		self.increment = increment
		self.minimum = minimum
		self.cleanup = []

	def set_cleanup(self, trigger):
		"""Set a trigger to be cancelled (deleted) when the value of
		targetkey reaches zero"""
		self.cleanup.append(trigger)

	def change(self, key, old, new):
		if new >= old:
			return
		diff = old - new
		newval = self.parent[self.targetkey] + diff * self.increment
		self.parent[self.targetkey] = max(0, newval)
		if newval == 0:
			for t in self.cleanup:
				t.unregister()
