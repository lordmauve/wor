#########

from Database import DB
from Logger import log, exception_log
from Triggerable import Triggerable
import pickle
import pickletools
import copy
import psycopg2
import Util
import types

from Strategied import Strategied


class SerObject(Triggerable, Strategied):
	"""This is the base class for all objects that might end up in the database."""

	@classmethod
	def load(cls, id, allprops=False):
		"""Get the SerObject with the given id from the database"""

		#log.debug("Request to load " + str(id) + " from " + cls._table)

		if id in cls.cache_by_id:
			obj = cls.cache_by_id[id]
			#log.debug("... found in cache, returning " + str(obj))
			#log.debug("Cache is " + str(cls.cache_by_id))
			return obj

		try:
			cur = DB.cursor()
			cur.execute('SELECT id, state FROM ' + cls._table
						+ ' WHERE id=%(id)s',
						{ 'id': id }
						)
			row = cur.fetchone()
		except psycopg2.Error, dbex:
			exception_log.info("Database exception:" + str(dbex) + "\n")
			return None

		if row is None:
			return None

		obj = cls._load_from_row(row, allprops)
		#log.debug("... found in database, returning " + str(obj))
		#log.debug("Cache is " + str(cls.cache_by_id))
		return obj

	@classmethod
	def _load_from_row(cls, row, allprops):
		obj = pickle.loads(row[1])

		if allprops:
			# Fetch all properties of the object immediately (rather
			# than on demand)
			try:
				cur = DB.cursor()
				cur.execute('SELECT key, type, ivalue, fvalue, tvalue'
							+ ' FROM ' + cls._table + '_properties'
							+ ' WHERE ' + cls._table + '_id=%(id)s',
							{ 'id': row[0] }
							)
				prop = cur.fetchone()
				while prop is not None:
					obj._set_prop_from_row(prop)
					prop = cur.fetchone()
			except psycopg2.Error, dbex:
				exception_log.info("Database exception:" + str(dbex) + "\n")
				return None
		
		obj._id = int(row[0])
		obj._setup()
		obj._cache_object(obj)

		# Anything (member objects) which wants to be called after
		# load gets called here
		if hasattr(obj, '_on_load_objects'):
			for olo in obj._on_load_objects:
				olo.on_load()
			del(obj._on_load_objects)

		return obj

	def _set_prop_from_row(self, row):
		"""Set an object property from a DB row. Does not set the
		_changed property."""
		if row[1] == 'i':
			self.__dict__[row[0]] = row[2]
		elif row[1] == 'f':
			self.__dict__[row[0]] = row[3]
		elif row[1] == 't':
			self.__dict__[row[0]] = row[4]
		elif row[1] == 'b':
			self.__dict__[row[0]] = (row[2] == 1)
		#elif row[1] == 'p':
		#	self.__dict__[row[0]] = pickle.loads(row[5])

	@classmethod
	def _cache_object(cls, obj):
		"""Hook to allow classes to define their own caching scheme.
		Called after an object has been loaded and cached in
		cls.cache_by_id"""
		pass

	####
	# Saving the object to the database
	def save(self, force=False):
		"""Save to the database the parts of the object that have changed"""
		if not force and not self._changed:
			return
		if self._deleted:
			cur = DB.cursor()
			cur.execute('DELETE FROM ' + self._table
						+ ' WHERE id=%(id)s',
						{ 'id': self._id })
			self._changed = False
			return

		#log.debug("save " + self.ob_type() + str(self._id) + ": changed is " + str(self._changed_props))
		#log.debug("Full dump: " + str(self.__dict__))

		# The only time pickle() gets called is during save. We set up
		# for that event by constructing a set of property names that
		# we should pickle (rather than dump to the database table)
		self._pickle = set()

		# First, we iterate through the elements of the object that
		# have changed and save them. Anything which is not an atomic
		# type is punted for later
		params = { 'id': self._id }

		cur = DB.cursor()

		for key in self.__dict__.iterkeys():
			params['key'] = key
			params['value'] = self.__dict__[key]

			# Skip properties which begin with _
			if key[0] == '_':
				continue

			# Ignore/delete properties which are None
			if self.__dict__[key] is None:
				cur.execute('DELETE FROM ' + self._table + '_properties'
							+ ' WHERE ' + self._table + '_id=%(id)s'
							+ '   AND key=%(key)s',
							params)
				continue

			# Work out the type (and hence the DB serialisation) of
			# the object we're looking at
			typ = type(self.__dict__[key])
			if typ is int:
				params['type'] = 'i'
				value_field = 'ivalue'
			elif typ is float:
				params['type'] = 'f'
				value_field = 'fvalue'
			elif typ is str or typ is unicode:
				params['type'] = 't'
				value_field = 'tvalue'
			elif typ is bool:
				params['type'] = 'b'
				value_field = 'ivalue'
			elif issubclass(typ, SerObject):
				# This is a Bad Thing: complain about it lots
				log.error("The attribute '%s' contains a SerObject (%s). This combination cannot be pickled. Your attribute has not been stored at all. You should fix this as soon as possible." % (key, str(self.__dict__[key])))
			elif hasattr(self.__dict__[key], 'save'):
				# If the object has its own save() method, call that
				# as well, but still pickle it
				self.__dict__[key].save()
				self._pickle.add(key)
				continue
			else:
				# It's not an atomic type that we know about, or which
				# wants to handle itself, so we're going to pickle this
				# property into the central store, not write to the DB
				self._pickle.add(key)
				continue

			# If the key wasn't changed, we don't need to do anything
			if key not in self._changed_props:
				continue

			# At this point, we've got an atomic type we understand
			# and can put into *_properties, so we do so. The
			# following code is idiomatic for an insert-or-update in
			# postgres (as per
			# http://www.postgresql.org/docs/8.3/static/sql-update.html).
			cur.execute('SAVEPOINT update1')
			try:
				# Try an insert first.
				sql = 'INSERT INTO ' + self._table + '_properties'
				sql += ' (' + self._table + '_id, key, '
				sql += 'type, ' + value_field + ')'
				sql += 'VALUES (%(id)s, %(key)s, %(type)s, %(value)s)'
				cur.execute(sql, params)
			except psycopg2.Error, ex:
				# If the insert failed (due to a primary key
				# uniqueness violation), skip back and try an update
				# instead
				cur.execute('ROLLBACK TO SAVEPOINT update1')
				cur.execute('UPDATE ' + self._table + '_properties'
							+ ' SET ' + value_field + ' = %(value)s,'
							+ '	 type = %(type)s'
							+ ' WHERE ' + self._table + '_id = %(id)s'
							+ '   AND key = %(key)s',
							params)
			else:
				# If the insert succeeded, we need to tie off the
				# savepoint. If it failed, we don't have to do this,
				# as it was rolled back in the except: section above.
				cur.execute('RELEASE SAVEPOINT update1')

		# We;ve now saved the atomic types in this object. We now need
		# to save the complex types. This is done by pickling the
		# remains of the object, and saving it to the state field of
		# the * table. (Where * is the object type).  Note that we
		# rely on having set up the self._pickle container for this to
		# work.
		state = pickle.dumps(self, -1) # Use the highest pickle
									   # protocol we can

		sql = 'UPDATE ' + self._table + ' SET state=%(state)s'

		# We find out what additional indices we need to write to the
		# DB, and construct some SQL for them
		idx = self._save_indices()
		for iname in idx.iterkeys():
			sql += ', %(iname)s=%%(%(iname)s)s' % { 'iname': iname }

		sql += ' WHERE id=%(identity)s'

		# Add in the required parameters of identity and state
		idx['identity'] = self._id
		idx['state'] = psycopg2.Binary(state)

		# Update the DB
		cur = DB.cursor()
		cur.execute(sql, idx)
		
		self._changed = False

	def _save_indices(self):
		"""Return a dict of DB field names and values to write as
		additional indexes to the database"""
		return { }

	@classmethod
	def save_cache(cls):
		for oid, obj in cls.cache_by_id.iteritems():
			obj.save()

	####
	# Pickling (serialisation and deserialisation)
	def __getstate__(self):
		"""Save this object to a pickled state"""
		# Shallow-create a new dictionary based on our current one,
		# but leave out all the properties that start with "_", and
		# the properties that we've already saved to *_properties in
		# the DB. This relies on self._pickle having been set up
		# first. If it hasn't, something has gone terribly wrong, and
		# we've probably not been called through self.save().
		if not hasattr(self, '_pickle'):
			log.error("Failure in pickle for " + self.ob_type() + " " + str(self._id))
			# Panic! (See comment above). The usual cause of this
			# exception is storing a SerObject in foo.bar, where it
			# then gets pickled as foo is pickled, but without having
			# been passed through foo.bar.save(). Instead, use either
			# foo._bar or foo.bar = bar._id.
			raise AssertionError("You have probably stored a reference to a SerObject in an attribute that doesn't start with '_'. Check the logs for which attribute it is.")

		obj = {}
		for k in self._pickle:
			# We only take properties that don't start with "_", and
			# which weren't stored in the *_properties table
			if not k.startswith('_'):
				obj[k] = getattr(self, k)
		del(self._pickle)
		return obj

	def __setstate__(self, state):
		"""Load an object from a pickled state"""
		for k, v in state.iteritems():
			self.__dict__[k] = v

	####
	# Property access. Not directly related to object serialisation,
	# but needed by everything.
	def __getattribute__(self, key):
		"""This is called unconditionally on every attribute access.
		We maintain a list of all the properties that we have already
		sought and not found."""

		# FIXME: Test speed difference between all these lookups of
		# object.__getattribute__, and caching it as oga =
		# object.__getattribute__

		#log.debug("__getattribute__: " + str(key))

		# If it's a "special" property, use the normal access method
		if key[0] == '_':
			#log.debug(" ... " + key + " special property")
			return object.__getattribute__(self, key)
		
		# We look in the current object's dictionary first. If it's
		# there, we return it
		mydict = object.__getattribute__(self, "__dict__")
		if key in mydict:
			#log.debug(" ... " + key + " in dictionary: " + str(mydict[key]))
			return mydict[key]

		# FIXME: Peek in the class hierarchy first and see if it's
		# there and a callable (bound method?). If so, we can return
		# the callable directly. This will prevent DB lookups on
		# method calls. It will also prevent assignment of callables
		# to objects, but that's OK because we don't support
		# serialising them anyway, so we'd have to assign them to _foo
		# names to avoid killing the serialiser, and therefore we'd
		# never get this far in this method when accessing them.
		
		# If it's not there, we check to see whether it's a property
		# we've tried to load before and failed
		failed = object.__getattribute__(self, "_failed_props")
		if key not in failed:
			#log.debug(" ... looking in DB")
			# It's not in the object's dictionary, and it's not
			# something we've tried before and failed to load, so we
			# can try loading from the DB
			if object.__getattribute__(self, "_demand_load_property")(key):
				# We've found a property in the DB, so we can return
				# it
				#log.debug(" ... " + key + " found")
				return mydict[key]
			else:
				# We didn't find it in the DB, so set a failure on the
				# key
				#log.debug(" ... " + key + " missed")
				failed.add(key)
				
		# At this point, we know it's not in the object dictionary,
		# and it's not in the DB, so if it's anywhere, it's in the
		# class hierarchy as a class property. So we go looking for
		# it in the class hierarchy.
		#log.debug(" ... " + key + " going upstream")
		return Strategied.__getattribute__(self, key)

	def _demand_load_property(self, key):
		cur = DB.cursor()
		cur.execute('SELECT key, type, ivalue, fvalue, tvalue'
					+ ' FROM ' + self._table + '_properties'
					+ ' WHERE ' + self._table + '_id = %(id)s'
					+ '   AND key = %(key)s',
					{ 'id': self._id,
					  'key': key })
		row = cur.fetchone()
		if row is not None:
			self._set_prop_from_row(row)
			return True
		else:
			return False

	def __setattr__(self, key, value):
		"""Used to set a value via obj.key = value"""
		Triggerable.__setattr__(self, key, value)
		if key[0] != '_':
			self._changed = True
			self._changed_props.add(key)

	####
	# Construction
	def __init__(self):
		# Create a new record in the database for this object and get
		# its ID
		cur = DB.cursor()
		cur.execute('SELECT nextval(\'' + self._table +'_id_seq\');')
		row = cur.fetchone()
		self._id = row[0]
		cur.execute('INSERT INTO ' + self._table
					+ ' (id, state) VALUES (%(id)s, NULL)',
					{ 'id': self._id })
		self._setup()
		Triggerable.__init__(self)

	def _setup(self):
		"""Called after __init__ or after load()"""
		self._changed = False
		self._deleted = False
		self._changed_props = set()
		self._failed_props = set()
		if self._id not in self.__class__.cache_by_id:
			self.__class__.cache_by_id[self._id] = self
		else:
			log.error("Attempting to recache object with ID "
					  + str(self._id)
					  + ": cache holds "
					  + str(self.__class__.cache_by_id[self._id])
					  + " and we are " + str(self)
					  )

	####
	# Destruction
	def demolish(self):
		self._changed = True
		self._deleted = True

	def ob_type(self):
		return self.__class__.__name__

	####
	# REST API
	def build_context(self, ret, fields):
		"""Helper function for writing context_get methods. Take the
		list of fields, and add the corresponding attribute values of
		this object into the ret hash. If the value of the attribute
		has a context_get() method of its own, use that. If the value
		of the attribute is a method, call it (and assume that it has
		no additional parameters)."""
		for k in fields:
			try:
				# See if the attribute exists in the first place
				v = getattr(self, k)
			except AttributeError:
				# If it doesn't, don't worry
				pass
			else:
				if v is None:
					pass
				if k in ret:
					pass

				if hasattr(v, 'context_get'):
					# If the attribute is an object that understands
					# context_get, use that.
					ret[k] = v.context_get()
				elif isinstance(v, types.MethodType):
					# If the attribute is a method, call it (assuming
					# that it takes no parameters)
					# Note that it's a bound method, so already has
					# the implicit self parameter.
					ret[k] = str(v())
				else:
					# Otherwise, just return the data
					ret[k] = str(v)

		return ret
