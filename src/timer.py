import random
from threading import Timer


# https://stackoverflow.com/a/56169014
class ResettableTimer:
    def __init__(self, function, interval_lb=100, interval_ub=200):
        self.interval = (interval_lb, interval_ub)
        self.function = function
        self.timer = Timer(self._interval(), self.function)

    def _interval(self):
        # in millis
        return random.randint(*self.interval) / 1000

    def start(self):
        self.timer.start()

    def reset(self):
        try:
            self.timer.cancel()
        except:
            pass
        self.timer = Timer(self._interval(), self.function)
        self.timer.start()