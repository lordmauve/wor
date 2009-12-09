"""Installer tools for Mac platform"""

import os
import sys
import grp

import common_installer

def preconditions(args, variables):
	"""Test that the installation environment is correct, with the
	relevant software installed and running.
	"""
	if common_installer.preconditions(args, variables):
		try:
			grp.getgrnam(variables['GROUP_NAME'])
			return True
		except KeyError:
			print "Please create the WOR group in System Preferences/Accounts prior to running this script."
			return False
	else:
		return False

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
	common_installer.postgres(variables)

def users_groups(variables):
	"""Set up users, groups and file permissions."""

	# Users and groups are hideously complex to create on the command line
	# on OS X (stupid stupid Apple creatures).  We're just going to mandate
        # that they're created ahead of time since it's amazingly simple to do
        # so with the GUI


def apache(variables):
	"""Set up Apache, using the apache config file we've just created."""

	vhosts = os.path.join('/opt', 'local', 'apache2', 'conf', 'vhosts')
	if (os.path.isdir(vhosts)):
		infile = open(os.path.join('tools', 'setup', 'apache-config'), 'r')

		outfile_name = os.path.join(vhosts, 'wor')
		if os.path.exists(outfile_name):
			sys.stdout.write("Destination file %s exists. Overwrite? (y/N) " % (outfile_name,))
			result = sys.stdin.readline()
			if result[0] not in [ 'Y', 'y' ]:
				print "Aborting installation"
				sys.exit(0)
			os.unlink(outfile_name)
		
		outfile = open(outfile_name, 'w')
		for l in infile:
			outfile.write(l)
		outfile.close()

	# Restart Apache to pick up the new config
	os.system("/opt/local/etc/LaunchDaemons/org.macports.apache2/apache2.wrapper restart")

