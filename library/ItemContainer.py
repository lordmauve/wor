####
# ItemContainer

import psycopg2
from Database import DB
from Item import Item
from OnLoad import OnLoad
from Logger import log
import Context

class ItemContainer(OnLoad):
	"""Implements a generic container of items, serialised to the
	object-ownership table. This container supports caching of items,
	and demand-loading."""
	def __init__(self, parent, name="container"):
		super(ItemContainer, self).__init__(parent)
		self.parent = parent
		self.name = name
		self._item_ids = set()
		self._item_types = {}
		self._changes = set()

	####
	# Loading and saving
	def save(self):
		"""Called when its parent object is save()d"""
		# Update the database, using our list of changed fields
		cur = DB.cursor()
		params = {}
		params['owner_type'] = self.parent.ob_type()
		params['owner_id'] = self.parent._id
		params['container'] = self.name

		for itemid in self._changes:
			params['id'] = itemid
			if itemid in self._item_ids:
				# The item has been added to this container, so we
				# need to add it to the database
				try:
					# We try to insert. If it fails, we've already got
					# it in here.
					cur.execute('SAVEPOINT item_update')
					cur.execute('INSERT INTO item_owner'
								+ ' (item_id, owner_type, owner_id, container)'
								+ ' VALUES (%(id)s, %(owner_type)s,'
								+ '		 %(owner_id)s, %(container)s)',
								params)
				except psycopg2.Error, ex:
					# If the insert failed, we roll back the savepoint
					# just to keep it all sane.
					cur.execute('ROLLBACK TO SAVEPOINT item_update')
				else:
					# If the insert succeeded, we close the
					# savepoint. If it failed, we've rolled it back
					# already.
					cur.execute('RELEASE SAVEPOINT item_update')
			else:
				# The item is no longer in this container, so we need
				# to delete it from the database
				cur.execute('DELETE FROM item_owner'
							+ ' WHERE item_id = %(id)s'
							+ '   AND owner_type = %(owner_type)s'
							+ '   AND owner_id = %(owner_id)s'
							+ '   AND container_name = %(container)s',
							params)

	def __getstate__(self):
		"""Pickle this object. The contents of _item_ids and
		_item_types should already have been saved, via save()"""
		state = {}
		for k in self.__dict__.iterkeys():
			if k[0] != '_':
				state[k] = self.__dict__[k]
		return state

	def on_load(self):
		self._item_ids = set()
		self._item_types = {}
		self._changes = set()

		# Now load the contents of the container
		cur = DB.cursor()
		cur.execute('SELECT item.id, item.type'
					+ ' FROM item, item_owner'
					+ ' WHERE item.id = item_owner.item_id'
					+ '   AND item_owner.owner_type = %(owner_type)s'
					+ '   AND item_owner.owner_id = %(owner_id)s'
					+ '   AND item_owner.container = %(container)s',
					{ 'owner_type': self.parent.ob_type(),
					  'owner_id': self.parent._id,
					  'container': self.name })

		row = cur.fetchone()
		while row != None:
			# Update the list by ID
			self._item_ids.add(row[0])
			# Update the list by name
			if row[1] not in self._item_types:
				self._item_types[row[1]] = set()
			self._item_types[row[1]].add(row[0])
			row = cur.fetchone()

	####
	# REST API support
	def context_get_equip(self):
		"""Retrieve a table of the contents of this object for
		purposes of the REST API"""
		ret = []
		for itype, ilist in self._item_types.iteritems():
			for itemid in ilist:
				# FIXME: Get and return count
				textname = Item.get_class(itype).name_for(Context.context)
				ret.append((itype, itemid, textname))
				
		return ret

	####
	# Item access
	def __getitem__(self, key):
		if key is int:
			# We've been asked for an item by ID
			return self._item_ids[key]
		elif key is str:
			return self._item_types[key][:]
		else:
			raise TypeError()

	def __setitem__(self, key, value):
		raise KeyError()

	def __contains__(self, key):
		"""Tests whether an item is in the container, by ID. Use has()
		to test for the presence of items."""
		return key in self._item_ids

	def has(self, itemclass, count=1):
		"""Test whether the container has 'count' of items of type
		itemclass. itemclass must be a class object."""
		if itemclass.__name__ not in self._item_types:
			return False
		if itemclass.aggregate:
			total = 0
			for item in self._item_types[itemclass.__name__]:
				total += item.count
		else:
			total = len(self._item_types[itemclass.__name__])
		return total >= count

	def add(self, item):
		self._item_ids.add(item._id)
		itype = item.ob_type()
		if itype not in self._item_types:
			self._item_types[itype] = set()
		self._item_types[itype].add(item._id)
		self._changes.add(item._id)

	# FIXME: Write this function
	#def remove(self, item):
	#	self._changes.add(item._id)
