from persistent import Persistent
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from BTrees.OOBTree import OOBTree

from wor.db import db
from wor.items.base import Item, AggregateItem

from Logger import log
#import DBLogger
import Context
import Util


class ItemContainer(Persistent):
	"""Implements a generic container of items."""

	def __init__(self, parent, items=[]):
		self.parent = parent
		self.items = OOBTree()
		if items:
			self.add_items(items)

	def context_get_equip(self, context):
		"""Retrieve a table of the contents of this object for
		purposes of the REST API"""
		ret = []
		for ilist in self.items.values():
			for item in ilist:
				ret.append({
					'cls': item.internal_name(),
					'id': db.id(item),
					'description': item.description(),
					'count': item.count,
					'name': unicode(item),
				})

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
			item = db.get_for_id(key)
			try:
				if item in self.items[item.internal_name()]:
					return item
			except:
				raise KeyError("Item '%d' not found in container." % key)
		elif isinstance(key, str):
			i = self._get_first_item(key)
			if i is None:
				raise KeyError("No such item '%s' in container" % key)
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
		if isinstance(key, str):
			return key in self.items
		elif isinstance(key, long) or isinstance(key, int):
			return key in self._item_ids
		else:
			raise TypeError()

	def has(self, itype, count=1):
		"""Test whether the container has 'count' of items of type
		itemclass.

		Parameters:
		itemtype -- the class name of the item to look for.
		count -- the number of items to look for.
		
		Returns: True if the container contains at least 'count' items
		of class 'itemclass'.
		"""
		if itype not in self.items:
			return False

		# Since items have a count of 1 by default, we can just 
		# iterate through all of them.
		#
		# TODO: Figure out if there's a way to internalize this in 
		#       Item
		itemclass = Item.get_class(itype)
		if issubclass(itemclass, AggregateItem):
			# Note that we should only have a single aggregate of a 
			# given type per container
			total = sum([i.count for i in self.items[itype]])
		else:
			total = len(self.items[itype])

		return total >= count

	def create(self, itype, count=1):
		"""Create an item of type itype within this container,
		and return the instance created.

		If count is given, create the number specified - but only return
		the last instance created.
		"""
		icls = Item.get_class(itype)
		if issubclass(icls, AggregateItem):
			inst = icls(count=count)
			self.add(inst)
		else:
			for i in xrange(count):
				inst = icls()
				self.add(inst)
		return inst

	def add(self, item):
		"""Add the given item to the container.

		Parameters:
		item -- The item to add.
		"""

		# Get the type from the item
		itype = item.internal_name()
		
		shouldDiscard = False

		# get the first element of the type.
		existing_item = self._get_first_item(itype)
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
			item.destroy()
			# We don't need to set any changes here, as we've only
			# updated the internal state of existing_item, and not
			# modified the container itself.
		else:
			# If we're not discarding the new item, it should be added
			# to the container, and its ownership updated.
			item.set_owner(self.parent)
			self.items.setdefault(itype, PersistentList()).append(item)
#			DBLogger.log_item_event(DBLogger.ITEM_ADD, item._id,
#									container=self)

	def add_items(self, ilist):
		"""Add a list of items to the container.

		Parameters:
		ilist -- an iterable list of items to add
		"""
		for i in ilist:
			self.add(i)

	def take(self, itype, count=1):
		"""Remove items arbitrarily from the container.

		Parameters:
		itemclass -- the class of item to remove
		count -- the number of items to remove
		Returns:
		A set containing the items removed.
		Raises:
		WorInsufficientItemsError if there are not enough items in
		this inventory container to fulfil the request.
		"""
		# Try splitting the item
		first_item = self._get_first_item(itype)
		if first_item is None:
			raise Util.WorInsufficientItemsException("No %s in container. Could not remove %d items." % (itype, count))
		split_item = first_item.split(count)

		rv = None
		if split_item is None:
			# We can't split, so we've got a singular item class: grab
			# the first count items from the list and remove them
			items = self.items[itype]
			rv, remaining_items = items[:count] + items[count:]

			if len(rv) < count:
				raise Util.WorInsufficientItemsException(
					"Attempted to remove %d items of type %s, but only %d were found"
					% (count, itype, len(rv)))

			if remaining_items:
				self.items[itype] = remaining_items
			else:
				del self.items[itype]
		else:
			# We successfully split, so return the result
			rv = set([split_item,])

		return rv

	def remove(self, item):
		"""Removes the given item from the container, and returns it.
		"""
		itype = item.internal_name()
		items = self.items[itype]
		items.remove(item)
		item.set_owner(None)
#		DBLogger.log_item_event(DBLogger.ITEM_REMOVE, item._id,
#								container=self)
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

	def _get_first_item(self, itype):
		"""Get an arbitrary item of the given type from the container.

		Parameters:
		itype -- an item type name.
		Returns: an arbitrary item of that type from the container, or
		None if no item of that type is present
		"""
		try:
			return self.items[itype][0]
		except KeyError:
			return None

	def transfer_to(self, item, destination, count=1):
		"""Transfer an item from this container to another.

		Parameters:
		item -- The item to move
		destination -- The target container
		count -- The number of units to move, if the item is aggregate

		Raises: WorInsufficientItemsError if there are not enough
		items in this inventory container to fulfil the request.
		"""
		split_item = self.split_or_remove(item, count)
		destination.add(split_item)

	def bulk_transfer_to(self, itemclass, destination, count=1):
		"""Transfer a number of items (chosen arbitrarily) of a given
		class to another container.

		Parameters:
		itemclass -- the class of item to transfer
		destination -- the target container
		count -- the number of units to move

		Raises: WorInsufficientItemsError if there are not enough
		items in this inventory container to fulfil the request.
		"""
		ilist = self.take(itemclass, count)
		destination.add_items(ilist)


class Inventory(ItemContainer):
	"""Inventory for an Actor; possibly does something with ownership?"""
