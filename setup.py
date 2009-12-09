#!/usr/bin/python

import os
import os.path
import re
import getpass
import sys
import pwd
import platform
import random

sys.path.append(os.path.join('tools', 'setup', platform.system()))
sys.path.append(os.path.join('tools', 'setup'))

import installer


class ConfVar(object):
	def __init__(self, key, prompt, default=''):
		self.key = key
		self.prompt = prompt
		self.default = default
		self.re = re.compile("@%s@" % self.key)

	def ask(self, write_defaults=None, standalone=False):
		if standalone:
			rv = self.ask_default()
		else:
			rv = self.ask_impl()
		if write_defaults is not None:
			write_defaults.write('"%s": """%s""",\n' % (self.key, str(self.value)))
		return rv

	def ask_default(self):
		self.value = self.default
		return True

	def ask_impl(self):
		"""Ask the user for input, return True if we pass validation.
		"""
		sys.stdout.write("%s (%s): " % (self.prompt, self.default))
		sys.stdout.flush()
		self.value = sys.stdin.readline()
		if self.value == "\n":
			self.value = self.default
		self.value = self.value.strip()
		return True

	def replace(self, line, state):
		return self.re.sub(str(self.value), line)

class CVFixed(ConfVar):
	def __init__(self, key, default):
		ConfVar.__init__(self, key, '', default)

	def ask_impl(self):
		self.value = self.default
		return True


class CVPasswordFixed(CVFixed):
	def __init__(self, key):
		pwd = ''
		while len(pwd) < 12:
			c = os.urandom(1)
			if c.isalnum() or c in "!$%^&*()_-=+:;{}[]@#~|<>,.?/":
				pwd += c
		CVFixed.__init__(self, key, pwd)


class CVPassword(ConfVar):
	def __init__(self, key, prompt):
		ConfVar.__init__(self, key, prompt, '')

	def ask_default(self):
		while len(pwd) < 12:
			c = os.urandom(1)
			if c.isalnum() or c in "!$%^&*()_-=+:;{}[]'@#~|<>,.?/":
				pwd += c
		self.value = pwd
		return True

	def ask_impl(self):
		self.value = getpass.getpass("%s:" % self.prompt)
		return True


class CVBoolean(ConfVar):
	def __init__(self, key, prompt, default=True):
		ConfVar.__init__(self, key, prompt, default)

	def _check_default(self):
		if self.default == "True":
			self.default = True
		elif self.default == "False":
			self.default = False

	def ask_default(self):
		self._check_default()
		self.value = self.default
		return True

	def ask_impl(self):
		self._check_default()
		if self.default:
			sys.stdout.write("%s (Y/n): " % (self.prompt,))
		else:
			sys.stdout.write("%s (y/N): " % (self.prompt,))
		sys.stdout.flush()
		self.value = sys.stdin.readline()
		if self.value[0] not in ('Y', 'y', 'N', 'n', '\n'):
			sys.stdout.write('Please enter Y or N\n')
			sys.stdout.flush()
			return False
		if self.value == "\n":
			self.value = self.default
		elif self.value[0] in ('Y', 'y'):
			self.value = True
		else:
			self.value = False
		return True

	def replace(self, line, state):
		if self.value:
			v = "1"
		else:
			v = "0"
		return self.re.sub(v, line)


class CVBlock(CVBoolean):
	def __init__(self, key, prompt, default=True):
		ConfVar.__init__(self, key, prompt, default)
		self.start = re.compile("^@%s\\[" % self.key)
		self.negative = re.compile("^@\\!%s\\[" % self.key)
		self.end = re.compile("^\\]%s@" % self.key)

	def replace(self, line, state):
		if self.start.search(line):
			state['output'] = self.value
			return ""
		elif self.negative.search(line):
			state['output'] = not self.value
			return ""
		elif self.end.search(line):
			state['output'] = True
			return ""
		return line


def help():
	print """Usage: setup.py [options]
Options:
	help		Print this help
	database	Set up postgres on this machine
	web			Set up Apache to run the game, or a terrain server, or both

If no options are given, both database and web will be set up.
"""
	sys.exit(0)


variables = [
	ConfVar('INSTALL_BASE', 'Base code installation', sys.path[0]),
	ConfVar('LOG_LOCATION', 'Location of log files', os.path.join(sys.path[0], 'logs')),
	ConfVar('DB_HOST', 'PostgreSQL database host', 'localhost'),
	ConfVar('DB_NAME', 'Database name', 'wor'),
	ConfVar('DB_USER', 'Database username', 'wor'),
	CVPasswordFixed('DB_PASS'),
	CVFixed('GROUP_NAME', 'wor'),
	ConfVar('DEV_USER', 'Your user name', ''),
	CVFixed('LANDSCAPE_SEED_1', random.randint(0, 1<<31)),
	CVBlock('TERRAIN_SERVER', 'Set up terrain server', True),
	CVBlock('USE_HTTPS', 'Configure authentication server with HTTPS', False),
	CVBlock('ENABLE_AUTHZ', 'Require authorisation for REST API interaction', True),
	]

value_by_key = {}

def template_substitution():
	try:
		from setup_defaults import setup_defaults
	except ImportError:
		setup_defaults = {}
	new_defaults = open(os.path.join(sys.path[0], "setup_defaults.py"), "w")
	new_defaults.write("setup_defaults = {\n")

	# We've got the list of prompts and variables, so ask about each of
	# them in turn
	for v in variables:
		if setup_defaults.get(v.key) != None:
			v.default = setup_defaults.get(v.key)
		while not v.ask(new_defaults):
			sys.stdout.write("Got value for " + v.key + " " + str(v.value))
			sys.stdout.flush()
		value_by_key[v.key] = v.value

	new_defaults.write("}\n")
	new_defaults.close()

	# Now do the substitutions
	for path, dirs, files in os.walk(value_by_key['INSTALL_BASE']):
		for f in files:
			if os.path.splitext(f)[1] != ".template":
				continue

			source_name = os.path.join(path, f)
			dest_name = os.path.splitext(source_name)[0]

			infile = open(source_name, "r")
			outfile = open(dest_name, "w")
			state = { 'output': True }
			for line in infile:
				for v in variables:
					line = v.replace(line, state)
				if state['output']:
					outfile.write(line)

			infile.close()
			outfile.close()


# Validate the installation parameters
valid_params = ( 'web', 'database' )
args = sys.argv[1:]
for p in args:
	if p == "help" or p not in valid_params:
		help()

if len(args) == 0:
	args = [ 'web', 'database' ]

# NOTE: Moved the template substitutions here, so we can set up preconditions 
#       based on variables (Darwin has one case where that's useful.  Okay, it's
#       a hack.  Still... (DWB 11/30/09)
template_substitution()

if not installer.preconditions(args, value_by_key):
	sys.exit(1)

# Set up postgres
if "database" in args:
	print "\nSetting up database\n"
	installer.postgres(value_by_key)

# Add user/group membership -- only necessary for apache server to
# write to log files and cache files.
if "web" in args:
	print "\nSetting up web server\n"
	installer.users_groups(value_by_key)

	# Get the names of the files/dirs to allow the server to write to
	terrain_dir = os.path.join(value_by_key['INSTALL_BASE'],
							   'server_root', 'img', 'terrain')
	files = []
	# These are the subdirs that are present in an image-server directory
	cache_dirs = [ 'cache', 'component', 'fragment' ]
	for d in os.listdir(terrain_dir):
		path = os.path.join(terrain_dir, d)
		# Check whether we've found an image-server dir
		if (os.path.isdir(d)
			and os.path.isdir(os.path.join(d, 'cache'))):
			# If we have, add the subdirs to the list
			files += [ os.path.join(d, f) for f in cache_dirs ]

	# Add the oid store and the log directory
	files.append(os.path.join(value_by_key['INSTALL_BASE'], 'oid_store'))
	files.append(value_by_key['LOG_LOCATION'])

	# Set permissions
	installer.permissions(value_by_key, files)

	# Set up apache itself
	installer.apache(value_by_key)

