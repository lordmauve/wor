######
# Logger

import os
import sys
import logging
import BaseConfig
from Database import DB
import Context

# Set up a generic debug log
log = logging.getLogger('wor')
log.setLevel(logging.DEBUG)

filelog = logging.FileHandler(os.path.join(BaseConfig.log_dir, "debug"))
filelog.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
filelog.setFormatter(formatter)
log.addHandler(filelog)

# Set up a separate log to filter exceptions to
exception_log = logging.getLogger('wor-exceptions')
exception_log.setLevel(logging.DEBUG)
exfile = logging.FileHandler(os.path.join(BaseConfig.log_dir, "exceptions"))
exfile.setLevel(logging.DEBUG)

exfile.setFormatter(formatter)
exception_log.addHandler(exfile)


header = "%(stamp)f/%(req)s: "

####
# Logging specific event types to database
def log_raw_action(actid, params):
	"""Log a request for an action"""
	cur = DB.cursor()

	param_pairs = map(lambda k, v: str(k) + "=" + repr(v),
					  params.iterkeys(),
					  params.iteritems())

	sql_params = { 'stamp': Context.request_time,
				   'req': Context.request_id,
				   'act': actid,
				   'name': actid.split('.')[2],
				   'params': param_pairs.join(' ')
				   }
	
	cur.execute("INSERT INTO log_raw_action"
				+ " (stamp, request_id, action_id, action_name, parameters)"
				+ " VALUES (%(stamp)s, %(req)s, %(act)s, %(name)s, %(params)s)",
				sql_params)
	log.info((header + "ACTION %(act)s %(params)s") % sql_params)

ITEM_MERGE = "merge"
ITEM_SPLIT = "split"
ITEM_ADD = "add"
ITEM_REMOVE = "remove"

def log_item_event(type):
	"""Log an item event"""
	cur = DB.cursor()
	sql_params = { 'stamp': Context.request_time,
				   'req': Context.request_id }
	# FIXME: What DB structure are we going to need here?
	cur.execute("INSERT INTO log_item_event"
				+ " (stamp, request_id)"
				+ " VALUES (%(stamp)s, %(req)s)",
				sql_params)
	log.info((header + "ITEM") % sql_params)

def log_location_event():
	"""Log a location event"""
	# FIXME: fill in code here
	pass

def log_actor_event():
	"""Log an actor event/trigger"""
	# FIXME: fill in code here
	pass
