class JSONSerialisable(object):
	"""A mix-in class that provides tools for serialising to a JSON
	object (actually a python dict intended for JSON)"""

	def context_get(self, context):
		"""Helper function for writing context_get methods. Take the
		list of fields, and add the corresponding attribute values of
		this object into the ret hash. If the value of the attribute
		has a context_get() method of its own, use that. If the value
		of the attribute is a method, call it (and assume that it has
		no additional parameters)."""
		ret = {}
		if hasattr(self, 'context_fields'):
			for k in self.context_fields:
				v = getattr(self, k)
				if hasattr(v, 'context_get'):
					# If the attribute is an object that understands
					# context_get, use that.
					try:
						ret[k] = v.context_get(context)
					except TypeError:
						ret[k] = v.context_get()
				elif callable(v):
					result = v()
					if isinstance(result, list):
						ret[k] = [i.context_get(context) for i in result]
					else:
						ret[k] = v()
				else:
					ret[k] = str(v)
			return ret
			
		for k, v in self.__dict__.items():
			if k.startswith('_'):
				continue

			if hasattr(v, 'context_get'):
				# If the attribute is an object that understands
				# context_get, use that.
				try:
					ret[k] = v.context_get(context)
				except TypeError:
					ret[k] = v.context_get()
			else:
				ret[k] = str(v)
		return ret
