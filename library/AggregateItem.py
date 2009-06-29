########
# An aggregate item

import Item
import Logger
import Util

class AggregateItem(Item.Item):
	"""An item containing a number of identical objects.  Note that it 
           contains the underlying stuff in a conceptual sense only - rather 
	   than containing 500 Gold objects, for example, it's simply a Gold 
	   object with a 500 count"""
	aggregate = True

	def merge(self, new_item):
		"""Merge the given item with this item, if possible.  Return 
		  True if the new item should be discarded, False otherwise"""
		
		# Make sure we're merging an object of the proper type
		#
		# TODO: Is this good, or do we need to support subclasses as 
		#       well?
		if self.ob_type() == new_item.ob_type():
			self.count += new_item.count
			
			# FIXME: the log_item_event table appears to be 
			#        nonexistent atm
			#Logger.log_item_event(Logger.ITEM_MERGE)
			return True
		else:
			raise WorError("Incompatible types ("
				       + self.ob_type()
				       + "/"
				       + new_item.ob_type()
				       + ") cannot be merged")


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
			raise WorError("Cannot split " 
				       + num_items
				       + " items from an aggregate with only "
				       + self.count
				       + " items")
		else:
			# Clone this object
			new_obj = deepcopy(self)

			# And adjust the counts accordingly
			new_obj.count = num_items
			self.count -= num_items

			# Log the split
			Logger.log_item_event(ITEM_SPLIT)
			return new_obj
