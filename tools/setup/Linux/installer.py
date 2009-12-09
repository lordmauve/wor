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

import common_installer

def preconditions(args, variables):
	"""Test that the installation environment is correct, with the
	relevant software installed and running.
	"""
	
	return common_installer.preconditions(args, variables)

def permissions(variables, files):
	"""Set file permissions on the files we're passed, so that Apache
	can write to them.
	"""
	common_installer.permissions(variables, files)

def create_database(db, variables, suffix=""):
	"""Create a database instance.
	"""
	common_installer.create_database(db, variables, suffix)

def set_up_database(db, variables, sql_file, suffix=""):
	common_installer.set_up_database(db, variables, sql_file, suffix)

def postgres(variables):
	"""Set up the database: Users, databases and schemas."""
	common_installer.postgress(variables)

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
