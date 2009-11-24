########
# An aggregate item

from Item import Item
import DBLogger
import Util

class AggregateItem(Item):
	"""An item containing a number of identical objects.  Note that it 
           contains the underlying stuff in a conceptual sense only - rather 
	   than containing 500 Gold objects, for example, it's simply a Gold 
	   object with a 500 count"""
	aggregate = True

	def __init__(self, count=1):
		"""Create a new AggregateItem with the given unit count."""
		Item.__init__(self)
		self.count = count

	def merge(self, new_item):
		"""Merge the given item with this item, if possible.  Return 
		  True if the new item should be discarded, False otherwise"""

		# Make sure we're merging an object of the proper type
		#
		# TODO: Is this good, or do we need to support subclasses as 
		#       well?
		if self.ob_type() == new_item.ob_type():
			oq = self.count
			self.count += int(new_item.count)
			DBLogger.log_item_event(DBLogger.ITEM_MERGE,
									self._id,
									other_item=new_item._id,
									orig_quantity=oq,
									new_quantity=self.count)
			return True
		else:
			raise Util.WorError("Incompatible types (%s/%s) cannot be merged"
								% (self.ob_type(), new_item.ob_type()))
		return False

	def split(self, num_items):
		"""Splits the given number of items from this item.  If this is 
		   an aggregate, the split instance should be returned.  If 
		   not, None will be returned"""

		# Make sure we don't split more objects than we have.  If 
		# someone comes up with an aggregate that can be split into 
		# more instances than you originally had, then refactor this 
		# code.  I'll be in the corner trying to keep my head from 
		# exploding
		if self.count < num_items:
			raise Util.WorInsufficientItemsException(
				"Cannot split %d items from an aggregate with only %d items"
				% (num_items, self.count))
		else:
			# Clone this object
			new_obj = deepcopy(self)

			# And adjust the counts accordingly
			oq = self.count
			new_obj.count = num_items
			self.count -= num_items

			# Log the split
			DBLogger.log_item_event(DBLogger.ITEM_SPLIT,
									self._id,
									other_item=new_obj._id,
									orig_quantity=oq,
									new_quantity=self.count)
			return new_obj

		return None
