# coding: utf-8

########

import SerObject
import Actor
import Location
import Util

class Item(SerObject.SerObject):
	"""An item. By default, all items are unique. Some items are
	'aggregate' and represent a block of otherwise identical things --
	e.g. coins -- and can be combined and split (see AggregateItem).
	"""
	_table = "item"
	cache_by_id = {}
	class_cache_by_name = {}

	# Default failure function is a mean life of 300, and equal
	# probability of failing on each use.
	break_profile = lambda life: weibull(life, 300.0, 1.0)

	name = "Item"
	aggregate = False

	# Failure-rate (aka hazard) functions: return the probability
	# [0.0, 1.0) that this item will fail, given a lifetime of x
	@staticmethod
	def weibull(x, k, l):
		"""Weibull failure function, with position l and shape k.  The
		mean of this distribution is l*Γ(1+1/k)."""
		return k/l * math.pow(x/l, k-1.0)

	@classmethod
	def name_for(cls, player, count=1):
		if count > 1:
			if hasattr(cls, plural):
				return cls.plural
			else:
				return cls.name + "s"
		return cls.name

	@classmethod
	def get_class(cls, name):
		"""Obtain and cache an item class object by name"""
		if name in cls.class_cache_by_name:
			return cls.class_cache_by_name[name]
		# Load the containing module
		mod = __import__(name, globals(), locals(), [name], -1)
		# Cache the class from that module -- assumes all classes have
		# the exact same name as their containing module
		cls.class_cache_by_name[name] = mod.__dict__[name]
		return cls.class_cache_by_name[name]

	####
	# Add the indices for saving this object
	def _save_indices(self):
		idxs = super(Item, self)._save_indices()
		idxs['type'] = self.type()
		return idxs
	
	def owner(self):
		"""Return the owner of this object, loading it if necessary"""
		if self._owner == None:
			if self.owner_type == 'Actor':
				self._owner = Actor.load(self.owner)
			elif self.owner_type == 'Location':
				self._owner = Location.load(self.owner)
			elif self.owner_type == 'Item':
				self._owner = Item.load(self.owner)
			else:
				pass
		return self._owner

	def power(self, name):
		return Util.default(self[name])

	def destroy(self):
		"""Destroy this item, recycling it if necessary"""
		self.demolish()

	def try_break(self):
		"""Test this item for breakage, and return True if it broke"""
		if random.random() < self.break_profile(self.lifetime):
			# Then we broke. You may cry.
			self.destroy()
			return True

		return False
