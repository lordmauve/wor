#######
# Underlying database storage

import time
import psycopg2
import DBAuth

import sys
import traceback

DB = psycopg2.connect(host = DBAuth.host,
					  database = DBAuth.name,
					  user = DBAuth.user,
					  password = DBAuth.passwd)

# Put us in serialisation mode: every transaction occurs as if in some
# definite order w.r.t the other transactions
DB.cursor().execute("SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL SERIALIZABLE")

from Logger import log, exception_log

# We may get an objection from the database at any point (i.e. if some
# other transaction get in the way), so we have to be prepared to
# re-execute a transaction. This function handles that process for us.
# All server requests should be run through this function. The
# function should probably be a lambda calling the actual work
# function with the right parameters.
def retry_process(process):
	complete = False
	attempts = 5
	ret = False
	while not complete and attempts > 0:
		xact = DB.cursor()

		try:
			ret = process()
			DB.commit()
			complete = True
		except Exception, ex:
			log.debug("Exception!: " + str(type(ex)))
			msg = traceback.format_exception(*(sys.exc_info()))
			log.error(''.join(msg))
			attempts -= 1
			DB.rollback()
			time.sleep(5)
			
		# FIXME: This doesn't necessarily throw any exceptions if
		# there's a collision. Instead, the second process to get to
		# the locked record hangs until the first process
		# commits. When the first process commits (or rolls back), the
		# second process may _attempt_ to update. This needs more
		# think -- possibly explicit locking. Talk to gdb/rph about
		# what we can do?

	return ret
