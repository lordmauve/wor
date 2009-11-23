####
# ItemContainer

import psycopg2

from Database import DB
from Item import Item
from OnLoad import OnLoad
from Logger import log
import Context
import Util

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
				# Make sure to remove the item from our internal
				# collections as well
				self._item_ids.remove(item_id)
				for item_ids in self._item_types.values():
					if item_id in item_ids:
						item_ids.remove(item_id)

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
		while row is not None:
			# Update the list by ID
			self._item_ids.add(row[0])
			# Update the list by name
			iset = self._item_types.setdefault(row[1], set())
			iset.add(row[0])
			row = cur.fetchone()

	####
	# REST API support
	def context_get_equip(self):
		"""Retrieve a table of the contents of this object for
		purposes of the REST API"""
		ret = []
		for itype, ilist in self._item_types.iteritems():
			for itemid in ilist:
				item_class = Item.get_class(itype)
				textname = item_class.name_for(Context.context)

				item = Item.load(itemid)
				ret.append((itype, itemid, item.count, textname))

		return ret

	####
	# Item access
	def __getitem__(self, key):
		"""Find an (arbitrary) item in the container, and return that
		item without removing it from the container.

		Parameters:
		key -- one of: the unique ID of the item to retrieve, or
		               the name of an item type
		Returns: If key is an item ID, return that specific item, or
		raise KeyError if the item does not exist.
		If the key is an item type name, return a copy of the set of
		items with that type name in the container.
		"""
		# FIXME: Allow a class to be passed as key, as well
		if isinstance(key, long) or isinstance(key, int):
			# We've been asked for an item by ID
			if key in self._item_ids:
				return Item.load(key)
			else:
				raise KeyError()
		elif isinstance(key, str):
			return self._item_types[key].copy()
		else:
			raise TypeError()

	def __setitem__(self, key, value):
		raise KeyError()

	def __contains__(self, key):
		"""Tests whether a specific item is in the container, by ID.

		Parameters:
		key -- item or item ID to test
		Returns: True if the container holds the item with the given id

		Use has() to test for the presence of items by class.
		"""
		if isinstance(key, Item):
			return key._id in self._item_ids
		elif isinstance(key, long) or isinstance(key, int):
			return key in self._item_ids
		else:
			raise TypeError()

	def has(self, itemclass, count=1):
		"""Test whether the container has 'count' of items of type
		itemclass.

		Parameters:
		itemclass -- the class of the item to check for. Must be a leaf
		             class (base classes will not be counted).
		count -- the number of items to look for.
		
		Returns: True if the container contains at least 'count' items
		of class 'itemclass'.
		"""
		if itemclass.__name__ not in self._item_types:
			return False

		# Since items have a count of 1 by default, we can just 
		# iterate through all of them.
		#
		# TODO: Figure out if there's a way to internalize this in 
		#       Item
		if itemclass.aggregate:
			# Note that we can only have a single aggregate of a 
			# given type per container
			total = self.__get_first_item(itemclass.__name__).count
		else:
			total = len(self._item_types[itemclass.__name__])

		return total >= count

	def add(self, item):
		"""Add the given item to the container.

		Parameters:
		item -- The item to add.
		"""

		# Get the type from the item
		itype = item.ob_type()
		
		shouldDiscard = False

		# get the first element of the type.
		existing_item = self.__get_first_item(itype)
		if existing_item is not None:
			# Now, try to merge the new item into it.  Note that if
			# this is an aggregate, we'll only have one element in the
			# set. If it's not, there'll be no need to merge anyhow,
			# so we can get away with only eyeballing the first
			# element.
			shouldDiscard = existing_item.merge(item)

		# If merge does not indicate we should discard the element, add
		# it to our ID and type collections
		if shouldDiscard:
			item.demolish()
			# We don't need to set any changes here, as we've only
			# updated the internal state of existing_item, and not
			# modified the container itself.
		else:
			# If we're not discarding the new item, it should be added
			# to the container, and its ownership updated.
			self._item_ids.add(item._id)
			self._item_types[itype].add(item._id)
			self._changes.add(item._id)
			item.set_owner(self.parent)

	def remove(self, item):
		"""Removes the given item from the container, and returns it.
		"""
		self._item_types[item.ob_type()].remove(item._id)
		self._changes.add(item._id)
		self._item_ids.remove(item._id)
		item.set_owner(None)
		return item
	
	def split(self, item, num_items):
		"""Splits the given number of items from this item, returning
		the split items.

		If the item is not an aggregate, nothing is returned.

		If the item held in the container becomes empty, remove it
		from the container.

		Parameters:
		item -- the item to split
		num_items -- the number of parts to split from it
		
		Returns: None if this item is not an aggregate. Otherwise, the
		split instance is returned."""
		rv = item.split(num_items)
		if item.count <= 0:
			self.remove(item).destroy()
		return rv

	def split_or_remove(self, item, num_items):
		split_item = self.split(item, num_items)
		if split_item is None:
			split_item = self.remove(item)
		return split_item

	def __get_first_item(self, itype):
		"""Get an arbitrary item of the given type from the container.

		Parameters:
		itype -- an item type name.
		Returns: an arbitrary item of that type from the container, or
		None if no item of that type is present
		"""
		items = self._item_types.setdefault(itype, set())
		try:
			item_id = iter(items).next()
		except StopIteration:
			item = None
		else:
			item = Item.load(item_id)

		return item
