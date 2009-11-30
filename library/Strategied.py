import Strategy

class Strategied(object):
	"""A mix-in class to provide the capability to override any
	methods with ones from an alternative, Strategy, class.
	"""
	def __setstate__(self, state):
		"""Called when loading an object from a pickled state."""
		# First, set the state as normal
		object.__setstate__(self, state)
		# Then set up _method_overrides from self.strategies
		self._method_overrides = {}
		for sob in self.strategies:
			self.__apply_strategy(sob)

	def __getattribute__(self, key):
		"""Called unconditionally on every attribute access.
		"""
		# Is this a strategy class method?
		try:
			overrides = object.__getattribute__(self, "_method_overrides")
		except AttributeError:
			return object.__getattribute__(self, key)

		if key in overrides:
			# Return a function that calls the actual strategy
			# function with the right parameters
			def call_strategy(*args, **keys):
				fn_list = overrides[key][:]
				first_function = fn_list.pop()
				# We add the implied self argument, since we're
				# dealing with functions and not bound instances
				args = (self,) + args
				# The result of this call is a
				# Strategy.next_function instance
				return first_function(self, fn_list, args, keys)
			return call_strategy

		return object.__getattribute__(self, key)

	def set_strategy(self, name, strategy):
		"""Set a strategy class.

		We keep one strategy object per attribute. We also maintain,
		for each overridden function, a list of functions from
		strategy objects.
		"""
		if not hasattr(self, "strategies"):
			self.strategies = []
		if not hasattr(self, "_method_overrides"):
			self._method_overrides = {}

		self.__remove_strategy(name)
		if strategy is not None:
			self.__add_strategy(name, strategy)

	def __remove_strategy(self, name):
		"""Remove a strategy class, if one exists.
		"""
		for sob in self.strategies:
			if sob.applied_to == name:
				# Enumerate the overriding methods in s, and remove them
				# from the methods lists.
				for m in sob.methods:
					fn = getattr(sob, m).im_func
					self._method_overrides[m].remove(fn)
				sob.removed(self)
				self.strategies.remove(sob)
				break

	def __add_strategy(self, name, sob):
		"""Add a strategy class. Does not overwrite any existing
		strategy class (and hence *must* be preceded by a
		__remove_strategy call).
		"""
		# Set the current strategy of that name
		sob.applied_to = name
		self.strategies.append(sob)
		self.__apply_strategy(sob)

	def __apply_strategy(self, sob):
		"""For each method in the strategy, add it to the tail of the
		functions list. Create the functions list with our original
		method, if it's empty.
		"""
		for m in sob.methods:
			# Can't use setdefault() here, as getattr(self, m) is
			# different if _method_overrides already has a key for m
			# in it, and setdefault() evaluates all its parameters.
			if m not in self._method_overrides:
				orig_fn = getattr(self, m).im_func
				self._method_overrides[m] = [Strategy.override(orig_fn)]
			self._method_overrides[m].append(getattr(sob, m).im_func)
		sob.applied(self)
