#########
# Timed counter: something happens to the counter every n seconds

import time

class SimpleTimedCounter(object):
    def __init__(self, value, interval, maximum, minimum=0, increment=1, last=time.time()):
        self.value = value
        self.interval = interval
        self.minimum = minimum
        self.maximum = maximum
        self.increment = increment
        self.last = last

    def onload(self):
        diff = time.time() - self.last
        if diff < 0:
            return

        increments = int(diff / self.interval)
        if increments <= 0:
            return

        self.value += increments * self.increment
        self.last += increments * self.interval
