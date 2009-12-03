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

class APCounter(Triggerable):
	"""An on-demand AP counter.

	We do not have a minimum AP because players are allowed to spend into AP debt.
	"""
	increment = 10
	def __init__(self, actor, initial=120, interval=60, maximum=240):
		self.actor = actor
		self.last_value = initial
		self.last_time = time.time()
		self.interval = interval
		self.maximum = maximum

	def recompute_value(self):
		"""Compute the current value based on the time difference."""
		diff = time.time() - self.last_time

		increments = int(diff / self.interval)
		if increments <= 0: # Bail out if we're less than interval
                            # seconds from the last update
			return self.last_value

		new_v = self.last_value + increments * self.increment

		# Clamp only if the value has risen past the maximum
		if new_v > self.maximum:
			if self.last_value < self.maximum:
				new_v = self.maximum
			else:
				new_v = self.last_value

		self.last_value = new_v
		self.last_time += increments * self.interval

		return new_v

	def get_value(self):
		return self.recompute_value()
		
	def set_value(self, ap):
		self.actor._p_changed = True
		self.last_value = ap

	value = property(get_value, set_value)

	def time_to_next(self):
		return int((self.last_time - time.time()) + 0.5) % self.interval

	def context_get(self):
		return {
			'value': self.value,
			'maximum': self.maximum,
			'time_to_next': self.time_to_next(),
			'interval': self.interval,
			'increment': self.increment,
		}
