"""Installer tools for Linux platform"""

import os
import sys
import subprocess
import grp
import pwd
import platform
import stat

import psycopg2
import psycopg2.extensions

def preconditions(args):
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

def users_groups(variables):
	"""Set up users, groups and file permissions."""
	# FIXME: Check to see which addgroup/adduser implementation is
	# present. Only Debian/Ubuntu uses addgroup and adduser like this.
	try:
		grp.getgrnam(variables['GROUP_NAME'])
	except KeyError:
		os.system("addgroup %(GROUP_NAME)s" % variables)
	else:
		print "Group %(GROUP_NAME)s already exists: not creating a new one" % variables

	try:
		pwd.getpwnam('www-data')
	except KeyError:
		print "No apache user found. Is it installed?"
	else:
		os.system("adduser www-data %(GROUP_NAME)s" % variables)

	if variables['DEV_USER'] != "":
		os.system("adduser %(DEV_USER)s %(GROUP_NAME)s" % variables)

def apache(variables):
	"""Set up Apache, using the apache config file we've just created."""
	# FIXME: This will probably only work on Debian and Ubuntu. Check
	# for other configurations, such as Fedora.	
	avail = os.path.join('/etc', 'apache2', 'sites-available')
	enabled = os.path.join('/etc', 'apache2', 'sites-enabled')
	if (os.path.isdir(avail) and os.path.isdir(enabled)):
		infile = open(os.path.join('tools', 'setup', 'apache-config'), 'r')

		outfile_name = os.path.join(avail, 'wor')
		if os.path.exists(outfile_name):
			sys.stdout.write("Destination file %s exists. Overwrite? " % (outfile_name,))
			result = sys.stdin.readline()
			if result[0] not in [ 'Y', 'y' ]:
				print "Aborting installation"
				sys.exit(0)
			os.unlink(outfile_name)
		
		outfile = open(outfile_name, 'w')
		for l in infile:
			outfile.write(l)
		outfile.close()

		linkfile_name = os.path.join(enabled, '100-wor')
		try:
			os.unlink(linkfile_name)
		except OSError:
			pass
		os.symlink(os.path.join('..', 'sites-available', 'wor'), linkfile_name)

	# Restart Apache to pick up the new config
	os.system("/etc/init.d/apache2 restart")
