"""Context for requests."""

import types
import time
import os
import thread
import threading


context = None

# Fake "Player" object to use as an admin context
class __FakeActor(object):
	def __init__(self):
		self.admin = True

ADMIN_CTX = __FakeActor()

# Administrator access
ADMIN = 0
# Owner access
OWNER = 1
# Access given to friends: entity visible
FRIEND_VISIBLE = 2
# Access given to friends: entity invisible
FRIEND_INVISIBLE = 3
# Default access, given to everyone else: entity visible
STRANGER_VISIBLE = 4
# Default access, given to everyone else: entity invisible
STRANGER_INVISIBLE = 5

class Context(object):
	def __init__(self, player):
		self.player = player

	def is_admin(self):
		return getattr(self.player, 'admin', False)

	def authz_actor(self, actor):
		"""Return the degree of data that can be returned w.r.t. the
		current context."""
		context = self.player

		if self.is_admin():
			return ADMIN

		if context == actor:
			return OWNER

		if context.loc() is actor.loc():
			return STRANGER_VISIBLE

		return STRANGER_INVISIBLE

	def authz_location(self, loc):
		"""Return the degree of data that can be returned w.r.t. the
		current context."""
		context = self.player
		if self.is_admin():
			return admin

		#if context._id == loc.owner()._id:
		#	return OWNER

		if context.loc().pos.hop_distance(loc.pos) <= context.power('sight'):
			return STRANGER_VISIBLE

		return STRANGER_INVISIBLE

	def authz_item(self, item):
		context = self.player
		if self.is_admin():
			return admin

		if context.has_item(item):
			return OWNER

		return STRANGER_INVISIBLE

	def visible(self, ctx):
		return ctx in [ADMIN, OWNER, FRIEND_VISIBLE, STRANGER_VISIBLE]


def all_fields(obj):
	"""Return all "interesting" properties of this object."""
	fields = dir(obj)
	# Filter out anything starting with _
	#fields = filter(lambda x: x[0] != '_' or x[1] != '_', fields)
	fields = filter(lambda x: x[0] != '_', fields)
	# Filter out methods
	fields = filter(lambda x: not isinstance(getattr(obj, x),
											 types.MethodType),
					fields)

	# Filter out other unwanted bits
	for f in ('cache_by_name', 'inventory'):
		if f in fields:
			fields.remove(f)

	return fields


class ThreadsafeSequence(object):
	"""This class implements a callable that returns sequential integers
	starting from start, and can be call by multiple threads without
	returning duplicate IDs.

	"""
	def __init__(self, start=0):
		self.request_sequence = start
		self.lock = threading.Lock()
	
	def next(self):
		lock.acquire()
		r = self.request_sequence
		self.request_sequence += 1
		lock.release()
		return r


class LogContext(threading.local):
	"""Thread-local context for a request.

	LogContext.id - a unique ID for log entries corresponding to a
	single request.
	LogContext.time - a timestamp in UTC for the request.
	"""
	sequence = ThreadsafeSequence()

	def __init__(self):
		self.time = time.time()
		self.id = "%d.init" % os.getpid()

	def generate(self):
		"""Reinitialise context with current time and next id."""
		self.time = time.time()
		self.id = '%d.%d' % (os.getpid(), self.sequence.next())

log_ctx = LogContext()

# Server configuration
terrain_dir = ""

def set_server_config(config):
	global terrain_dir
	terrain_dir = os.path.join(config['wor.root_path'],
							   'server_root',
							   'img',
							   'terrain')
