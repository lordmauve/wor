import os.path
import thread
import threading

from ZODB import DB, FileStorage
import transaction

from wor.world.world import World
from wor.accounts import AccountManager

from BaseConfig import base_dir


def db_root_object(name, cls):
	def __wrapped(self):
		try:
			inst = self.root()[name]
		except KeyError:
			inst = cls()
			self.root()[name] = inst
		return inst
	return __wrapped


class WoRDB(object):
	def __init__(self, filename='Data.fs'):
		self.storage = FileStorage.FileStorage(os.path.join(base_dir, filename))
		self.db = DB(self.storage)
		self.cache = threading.local()

	def root(self):
		"""Retrieve the ZODB root using one connection per thread"""
		try:
			return self.cache.root
		except AttributeError:
			try:
				self.cache.root = self.cache.conn.root()
			except AttributeError:
				self.cache.conn = self.db.open()
				self.cache.root = self.cache.conn.root()
			return self.cache.root

	def id(self, object):
		"""Retrieve a unique ID for the serialised object given.

		This may be a huge hack - after all, why are these not already Python ints?

		"""
		id = 0
		for c in object._p_oid:
			id = id * 256 | ord(c)
		return id

	def get_for_id(self, id):
		"""Retrieve a serialised object for the unique ID given.
		
		This may also be a huge hack.

		"""
		c = ''
		for i in xrange(8):
			c = chr(id & 0xff) + c
			id = id // 256
		self.root()
		return self.cache.conn.get(c)

	def abort(self):
		transaction.abort()

	def commit(self):
		transaction.commit()
	
	world = db_root_object('world', World)
	accounts = db_root_object('accounts', AccountManager)


db = WoRDB()
