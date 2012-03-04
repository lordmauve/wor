######
# Logger

import os
import logging

from Context import log_ctx

log_dir = '.'

# Set up a custom formatter class
class WoRLogFormatter(logging.Formatter):
    def __init__(self, *params):
        logging.Formatter.__init__(self, *params)

    def format(self, record):
        text = logging.Formatter.format(self, record)
        text = log_ctx.id + " " + text
        return text


# Set up a generic debug log
log = logging.getLogger('wor')
log.setLevel(logging.DEBUG)

filelog = logging.FileHandler(os.path.join(log_dir, "debug"))
filelog.setLevel(logging.DEBUG)

base_format = "%(asctime)s %(name)s %(levelname)s: %(message)s"
formatter = WoRLogFormatter(base_format)
filelog.setFormatter(formatter)
log.addHandler(filelog)

# Set up a separate log to filter exceptions to
exception_log = logging.getLogger('wor-exceptions')
exception_log.setLevel(logging.DEBUG)
exfile = logging.FileHandler(os.path.join(log_dir, "exceptions"))
exfile.setLevel(logging.DEBUG)

exfile.setFormatter(formatter)
exception_log.addHandler(exfile)

header = "%(stamp)f/%(req)s: "
