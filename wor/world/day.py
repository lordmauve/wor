import time

DAY_LENGTH = 341 * 60  # Length of an in-game day, in seconds


class Day(object):
    NIGHT = 'night'
    SUNRISE = 'sunrise'
    SUNSET = 'sunset'
    DAYTIME = 'daytime'

    @classmethod
    def _time(cls):
        """Return the time, expressed as a fraction of the day length.
        
        This is to allow weird and wonderful forms of timekeeping.
        """
        return (time.time() % DAY_LENGTH) / DAY_LENGTH

    @classmethod
    def _date(cls):
        """Return the date, expressed in days since the epoch."""
        return time.time() // DAY_LENGTH

    @classmethod
    def time_of_day(cls):
        """Return one of the time-of-day constants listed above."""
        day_frac = cls._time()
        if day_frac < 0.2 or day_frac > 0.8:
            return Day.NIGHT
        elif day_frac < 0.3:
            return Day.SUNRISE
        elif day_frac > 0.7:
            return Day.SUNSET
        return Day.DAYTIME
