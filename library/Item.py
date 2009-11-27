# coding: utf-8

import os
import os.path

from SerObject import SerObject
import Util
import BaseConfig
from Plan import Plan, makeable_plans
from ActionMake import ActionMake
import Context
import DBLogger

# We must do this to run the code that defines all possible plans.
# Can't be done in Plan, for circular reference reasons.
import Plans


class Item(SerObject):
	"""An item. By default, all items are unique. Some items are
	'aggregate' and represent a block of otherwise identical things --
	e.g. coins -- and can be combined and split (see AggregateItem).
	"""
	_table = "item"
	cache_by_id = {}
	class_cache_by_name = {}
	group = "General"

	# Default failure function is a mean life of 300, and equal
	# probability of failing on each use.
	break_profile = lambda life: weibull(life, 300.0, 1.0)

	aggregate = False
	count = 1

	# Failure-rate (aka hazard) functions: return the probability
	# [0.0, 1.0) that this item will fail, given a lifetime of x
	@staticmethod
	def weibull(x, k, l):
		"""Weibull failure function, with position l and shape k.  The
		mean of this distribution is l*Γ(1+1/k)."""
		return k/l * math.pow(x/l, k-1.0)

	@classmethod
	def name_for(cls, player=None, count=1):
		try:
			name = cls.name
		except AttributeError:
			name = cls.__name__.lower()
			
		if count > 1:
			if hasattr(cls, 'plural'):
				return cls.plural
			else:
				return name + "s"
		return name

	def __unicode__(self):
		return self.name_for()

	@classmethod
	def get_class(cls, name):
		"""Obtain and cache an item class object by name"""
		if name in cls.class_cache_by_name:
			return cls.class_cache_by_name[name]
		# Load the containing module
		mod = __import__("Items."+name, globals(), locals(), [name], -1)
		# Cache the class from that module -- assumes all classes have
		# the exact same name as their containing module
		cls.class_cache_by_name[name] = mod.__dict__[name]
		return cls.class_cache_by_name[name]

	@staticmethod
	def list_all_classes():
		"""Obtain a list of all item class names"""
		import Items
		from AggregateItem import AggregateItem
		items = []
		for k in dir(Items):
			v = getattr(Items, k)
			if (isinstance(v, type)
				and issubclass(v, Item)
				and v is not Item
				and v is not AggregateItem):
				items.append(v)

		return items

	def __init__(self):
		SerObject.__init__(self)
		DBLogger.log_item_event(DBLogger.ITEM_CREATE, self._id)

	####
	# Add the indices for saving this object
	def _save_indices(self):
		idxs = super(Item, self)._save_indices()
		idxs['type'] = self.ob_type()
		return idxs

	@classmethod
	def flush_cache(cls):
		cls.cache_by_id = {}
		cls.class_cache_by_name = {}
	
	def owner(self):
 		"""The notional owner of the item. For quantum items with
 		multiple owners, this will be the owner that last touched it.
 		"""
 		if self._owner is None and self.owner_type != "":
			# Get the module for the right type of object, loading the class
			mod = __import__(self.owner_type, globals(), locals(), [self.owner_type], -1)
			# Get a handle on the class itself
			cls = mod.__dict__[self.owner_type]
			# Use the class's load() method to load the owner object
			self._owner = cls.load(self.owner_id)
		return self._owner

	def set_owner(self, obj):
		self._owner = obj
		if obj is not None:
			self.owner_type = obj.__class__.__name__
			self.owner_id = obj._id
		else:
			self.owner_type = ""
			self.owner_id = -1

	def power(self, name):
		return getattr(self, name, 0)

	def destroy(self):
		"""Destroy this item, recycling it if necessary"""
		DBLogger.log_item_event(DBLogger.ITEM_DESTROY, self._id)
		self.demolish()

	def try_break(self):
		"""Test this item for breakage, and return True if it broke"""
		if random.random() < self.break_profile(self.lifetime):
			# Then we broke. You may cry.
			self.destroy()
			return True

		return False

	def external_actions(self, acts, player, name=None):
		"""Retrieve the set of actions that can be performed on this
		object whilst held."""
		# Build system
		plans = makeable_plans(player, self)
		for p in plans:
			act = ActionMake(player, self, p)
			acts[act.uid] = act

	def context_get(self, context):
		"""Return a dictionary of properties of this object, given the
		current authZ context"""
		ret = {}
		ret['id'] = str(self._id)
		ret['type'] = self.ob_type()

		auth = context.authz_item(self)
		if auth == Context.ADMIN:
			fields = Context.all_fields(self)
		elif auth == Context.OWNER:
			fields = ['name', 'damage', 'description']
		else:
			fields = ['name']

		return self.build_context(ret, fields)

	def merge(self, new_item):
		"""Merge the given item with this item, if possible.  Return 
		  True if the new item should be discarded, False otherwise"""
		return False
		  
	def split(self, num_items):
		"""Splits the given number of items from this item.  If this is 
		   an aggregate, the split instance should be returned.  If 
		   not, None will be returned"""
		return None


	####
	# Combat functions: Move this to a separate mix-in class?
	def pre_attack(self, victim):
		"""Called before any attack happens"""
		pass

	def base_damage_to(self, victim):
		"""Return the base damage of this weapon"""
		return self.damage

	def weapon_break(self, user, victim):
		"""Test for breakage after hitting someone. Return True if
		we've broken."""
		broken = user.unlucky(self.break_profile(life))
		self.uses += 1
		return broken

	def miss_actor(self, user, victim):
		"""What to do if we missed the victim"""
		pass
