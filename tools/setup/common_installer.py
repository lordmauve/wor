"""Installer tools used in common across multiple platforms.  Note that thie MAY
 need to be renamed if these tools aren't used in the Windows installer as well
"""
import os
import sys
import subprocess
import grp
import pwd
import platform
import stat

import psycopg2
import psycopg2.extensions

def preconditions(args, variables):
	"""Test that the installation environment is correct, with the
	relevant software installed and running.
	"""
	
	if os.geteuid() != 0:
		print "Setup should be run as root, in order to set up the database and Apache server."
		return False

	# FIXME: Check presence of Apache, mod_python, and a running
	# postgres, depending on the arguments.
	return True

def permissions(variables, files):
	"""Set file permissions on the files we're passed, so that Apache
	can write to them.
	"""
	for f in files:
		os.chmod(f, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
		os.chown(f, -1, grp.getgrnam(variables['GROUP_NAME'])[2])

def create_database(db, variables, suffix=""):
	"""Create a database instance.
	"""
	cur = db.cursor()
	
	variables['db_suffix'] = suffix
	success = False
	while not success:
		# PG doesn't allow CREATE DATABASE to be used inside a transaction
		# Python API doesn't allow there not to be a transaction
		# Hack, hack...
		sql = ("CREATE DATABASE %(DB_NAME)s%(db_suffix)s" \
			   + " OWNER %(DB_USER)s" \
			   + " ENCODING 'UTF8';\n") % variables
		try:
			cur.execute(sql)
		except psycopg2.ProgrammingError, ex:
			db.rollback()
			if str(ex).find('database "%(DB_NAME)s%(db_suffix)s" already exists' % variables) != -1:
				decision = None
				while decision is None:
					sys.stdout.write("The database %(DB_NAME)s%(db_suffix)s already exists: remove it? (y/N): " % variables)
					response = sys.stdin.readline()
					if response[0] in ('y', 'Y', 'n', 'N', '\n'):
						decision = (response[0] in ('y', 'Y'))
					else:
						print "Please respond Y or N"
				if decision:
					cur.execute("DROP DATABASE %(DB_NAME)s%(db_suffix)s" % variables)
				else:
					success = True
			else:
				raise ex
		else:
			success = True
	db.commit()

def set_up_database(db, variables, sql_file, suffix=""):
	db = psycopg2.connect(host = variables['DB_HOST'],
						  database = variables['DB_NAME'] + suffix,
						  user = variables['DB_USER'],
						  password = variables['DB_PASS'])
	cur = db.cursor()
	inf = open(sql_file, "r")
	sql = ""
	for line in inf:
		if line.startswith("--") or line.isspace():
			continue
		sql += line
		if line.endswith(";\n"):
			cur.execute(sql)
			sql = ""
	db.commit()
	db.close()

def postgres(variables):
	"""Set up the database: Users, databases and schemas."""
	try:
		postgres = pwd.getpwnam("postgres")
	except KeyError:
		sys.stderr.write("Could not find postgres user. Aborting.\n")
		sys.exit(1)

	# Turn into the postgres user, so we can connect to template1
	os.seteuid(postgres[2])

	sql_file = os.path.join('tools', 'setup', 'schema.sql')

	db = psycopg2.connect(database = "template1",
						  user = "postgres")
	db.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
	cur = db.cursor()
	sql = "CREATE ROLE %(DB_USER)s WITH UNENCRYPTED PASSWORD '%(DB_PASS)s';\n" % variables
	try:
		cur.execute(sql)
	except psycopg2.ProgrammingError, ex:
		db.rollback()
		if str(ex).find('role "%(DB_USER)s" already exists' % variables) != -1:
			decision = None
			while decision is None:
				sys.stdout.write("User %(DB_USER)s already exists. Change password instead? (y/N): " % variables)
				response = sys.stdin.readline()
				if response[0] not in ('Y', 'y', 'N', 'n', '\n'):
					print "Please respond Y or N"
				else:
					decision = (response[0] in ('Y', 'y'))
				
			if decision:
				sql = "ALTER ROLE %(DB_USER)s UNENCRYPTED PASSWORD '%(DB_PASS)s'" % variables
				cur.execute(sql)
		else:
			raise ex
	db.commit()

	create_database(db, variables)
	create_database(db, variables, suffix="_test")

	db.close()

	# Turn back to normal
	os.seteuid(0)

	set_up_database(db, variables, sql_file)
	set_up_database(db, variables, sql_file, "_test")
