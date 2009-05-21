#########
# Timed counter: something happens to the counter every n seconds

import time
from OnLoad import OnLoad

class SimpleTimedCounter(OnLoad):
	# FIXME: Add "power" property so that we can modify the interval
	# properly? (Or punt to a different class?)
	def __init__(self, parent, value, interval, maximum, minimum=0, increment=1, last=time.time()):
		super(SimpleTimedCounter, self).__init__(parent)
		self.value = value
		self.interval = interval
		self.minimum = minimum
		self.maximum = maximum
		self.increment = increment
		self.last = last

	def on_load(self):
		diff = time.time() - self.last
		if diff < 0:
			return

		increments = int(diff / self.interval)
		if increments <= 0:
			return

		self.value += increments * self.increment
		self.last += increments * self.interval

	def context_get(self):
		return { 'value': self.value,
				 'interval': self.interval,
				 'maximum': self.maximum,
				 'last': self.last
				 }
