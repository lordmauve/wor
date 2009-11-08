#########
# Timed counter: something happens to the counter every n seconds

import time
from OnLoad import OnLoad
from Triggerable import Triggerable

class SimpleTimedCounter(OnLoad, Triggerable):
	"""This class counts a value in increments of
	<code>increment</code>, every <code>interval</code> seconds, with
	maximum and minimum allowed values."""
	# FIXME: Add "power" property so that we can modify the interval
	# properly? (Or punt to a different class?)
	def __init__(self, parent, value, interval, maximum, minimum=0, increment=1, last=time.time()):
		OnLoad.__init__(self, parent)
		Triggerable.__init__(self)
		self.value = value
		self.interval = interval
		self.minimum = minimum
		self.maximum = maximum
		self.increment = increment
		self.last = last

	def on_load(self):
		diff = time.time() - self.last
		if diff < 0: # Bail out if we've gone backwards
			return

		increments = int(diff / self.interval)
		if increments <= 0: # Bail out if we're less than interval
                            # seconds from the last update
			return

		new_v = self.value + increments * self.increment
		new_v = min(new_v, self.maximum)
		new_v = max(new_v, self.minimum)
		self.value = new_v
		
		self.last += increments * self.interval

	def context_get(self):
		return { 'value': self.value,
				 'interval': self.interval,
				 'maximum': self.maximum,
				 'last': self.last
				 }
