######
# Logger

import os
import sys
import logging
import BaseConfig

log = logging.getLogger('wor')
log.setLevel(logging.DEBUG)

filelog = logging.FileHandler(os.path.join(BaseConfig.log_dir, "wor-log.txt"))
filelog.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
filelog.setFormatter(formatter)
log.addHandler(filelog)
