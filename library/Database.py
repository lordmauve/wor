#######
# Underlying database storage

import psycopg2
import DBAuth

DB = psycopg2.connect(host = DBAuth.host,
					  database = DBAuth.name,
					  user = DBAuth.user,
					  password = DBAuth.passwd)

# Put us in serialisation mode: every transaction occurs as if in some
# definite order w.r.t the other transactions
DB.cursor().execute("SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL SERIALIZABLE")

# We may get an objection from the database at any point (i.e. if some
# other transaction get in the way), so we have to be prepared to
# re-execute a transaction. This function handles that process for us.
# All server requests should be run through this function. The
# function should probably be a lambda calling the actual work
# function with the right parameters.
def retry_process(process):
	complete = False
	while not complete:
		xact = DB.cursor()
		try:
			xact.execute("BEGIN TRANSACTION")
			ret = process()
			xact.execute("COMMIT")
			complete = True
		except psycopg2.Error, dbex:
			xact.execute("ROLLBACK")

	return ret
