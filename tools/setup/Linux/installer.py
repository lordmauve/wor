"""Installer tools for Linux platform"""

import os
import sys
import subprocess
import grp
import pwd
import platform
import stat

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

def postgres(variables):
	"""Set up the database: Users, databases and schemas."""
	try:
		postgres = pwd.getpwnam("postgres")
	except KeyError:
		sys.stderr.write("Could not find postgres user. Aborting.\n")
		sys.exit(1)

	os.seteuid(postgres)
	
	psql = subprocess.Popen(["psql", "template1"],
							stdin=subprocess.PIPE,
							stdout=subprocess.PIPE,
							stderr=subprocess.STDOUT)
	psql.stdin.write("CREATE USER %(DB_USER)s WITH UNENCRYPTED PASSWORD '%(DB_PASS)s';\n" % variables)

	psql.stdin.write("CREATE DATABASE %(DB_NAME)s OWNER %(DB_USER)s ENCODING UTF8;\n" % variables)
	psql.stdin.write("\\c %(DB_NAME)s %(DB_USER)s\n" % variables)
	psql.stdin.write("\\i schema.sql\n")

	psql.stdin.write("CREATE DATABASE %(DB_NAME)s_test OWNER %(DB_USER)s ENCODING UTF8;\n" % variables)
	psql.stdin.write("\\c %(DB_NAME)s_test %(DB_USER)s\n" % variables)
	psql.stdin.write("\\i schema.sql\n")

	psql.stdin.write("\\q\n")
	
	os.seteuid(0)

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
		infile = open('apache-config', 'r')

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
