#########
# Timed counter: something happens to the counter every n seconds

import time

class SimpleTimedCounter(object):
    def __init__(self, value, interval, increment=1, last=time.time()):
        self.value = value
        self.interval = interval
        self.increment = increment
        self.last = last

    def on_load(self):
        diff = time.time() - self.last
        if diff < 0:
            return

        increments = int(diff / interval)
        if increments <= 0:
            return

        self.value += increments * self.increment
        self.last += increments * self.interval
