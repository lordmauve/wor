# coding: utf-8

########

import os
import os.path

from SerObject import SerObject
import Util
import BaseConfig
from Plan import Plan, makeable_plans
from ActionMake import ActionMake
import Context

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
	def name_for(cls, player=None, count=1):
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
		mod = __import__("Items."+name, globals(), locals(), [name], -1)
		# Cache the class from that module -- assumes all classes have
		# the exact same name as their containing module
		cls.class_cache_by_name[name] = mod.__dict__[name]
		return cls.class_cache_by_name[name]

	@staticmethod
	def list_all_classes():
		"""Obtain a list of all item class names"""
		# Get all the files in the Item directory
		cls_list = os.listdir(os.path.join(BaseConfig.base_dir, "content/Items"))
		# Filter out just the .py files
		cls_list = filter(lambda x: x.endswith(".py"), cls_list)
		cls_list = filter(lambda x: x[0] != '_', cls_list)
		# Remove the trailing .py and return
		return [ x[:-3] for x in cls_list ]

	####
	# Add the indices for saving this object
	def _save_indices(self):
		idxs = super(Item, self)._save_indices()
		idxs['type'] = self.ob_type()
		return idxs
	
	def owner(self):
		"""Return the owner of this object, loading it if necessary"""
		if self._owner == None:
			# Get the module for the right type of object, loading the class
			mod = __import__(self.owner_type, globals(), locals(), [self.owner_type], -1)
			# Get a handle on the class itself
			cls = mod.__dict__[self.owner_type]
			# Use the class's load() method to load the owner object
			self._owner = cls.load(self.owner_id)
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

	def external_actions(self, acts, player, name=None):
		"""Retrieve the set of actions that can be performed on this
		object whilst held."""
		# Build system
		plans = makeable_plans(player, self)
		for p in plans:
			act = ActionMake(player, self, p)
			acts[act.uid] = act

	def context_get(self):
		"""Return a dictionary of properties of this object, given the
		current authZ context"""
		ret = {}
		ret['id'] = str(self._id)
		ret['type'] = self.ob_type()

		auth = Context.authz_item(self)
		if auth == Context.ADMIN:
			fields = Context_all_fields(self)
		elif auth == Context.OWNER:
			fields = [ 'name', 'damage' ]
			#ret['description'] = self.description()
		else:
			fields = [ 'name' ]

		for k in fields:
			if k in ( 'cache_by_id' ):
				continue
			
			try:
				v = self[k]
			except KeyError:
				pass
			else:
				if v != None and k not in ret:
					if hasattr(v, 'context_get'):
						ret[k] = v.context_get()
					else:
						ret[k] = str(v)

		return ret
