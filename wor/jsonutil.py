import codecs
from django.http import HttpResponse
try:
	import json
except ImportError:
	try:
		import simplejson as json
	except ImportError:
		print >>sys.stderr, "simplejson is required for Python <2.6"
		print >>sys.stderr, "try easy_install simplejson or download from http://pypi.python.org/pypi/simplejson/"
		sys.exit(3)


class Everything(object):
	def __contains__(self, key):
		return True


class JSONSerialisable(object):
	"""A mix-in class that provides tools for serialising to a JSON
	object (actually a python dict intended for JSON)"""

	def context_authz(self, context):
		"""Returns a list of the context properties that can be
		seen in the given context, or None for no restriction."""
		return None

	def context_get(self, context):
		"""Helper function for writing context_get methods. Take the
		list of fields, and add the corresponding attribute values of
		this object into the ret hash. If the value of the attribute
		has a context_get() method of its own, use that. If the value
		of the attribute is a method, call it (and assume that it has
		no additional parameters)."""
		ret = {}
		
		# build authorised fields list
		auth = self.context_authz(context)
			
		if auth is None:
			auth = Everything()
		elif not isinstance(auth, Everything):
			auth = set(auth)

		if hasattr(self, 'context_fields'):
			# build the context from a list of fields
			for k in self.context_fields:
				if k not in auth:
					continue
				ret[k] = self.__context_property(getattr(self, k), context)
				v = getattr(self, k)

			# add in context_extra
			if hasattr(self, 'context_extra'):
				extra = self.context_extra(context)
				for k in extra:
					if k in auth:
						ret[k] = extra[k]
			return ret

		# fall back to building the context from the instance dictionary			
		for k, v in self.__dict__.items():
			if k not in auth or k.startswith('_'):
				continue
			ret[k] = self.__context_property(v, context, call_callables=False)
		return ret

	def __context_property(self, v, context, call_callables=True):
		"""Resolve the most appropriate context value for property"""
		if hasattr(v, 'context_get'):
			# If the attribute is an object that understands
			# context_get, use that.
			try:
				return v.context_get(context)
			except TypeError:
				return v.context_get()
		elif callable(v) and call_callables:
			result = v()
			if isinstance(result, list):
				return [i.context_get(context) for i in result]
			else:
				return self.__context_property(result, context, False)
		else:
			return v


class JSONResponse(HttpResponse):
	def __init__(self, blob):
		super(JSONResponse, self).__init__(mimetype='text/javascript; charset=UTF-8')
		utf8_out = codecs.getwriter('utf8')(self)
		json.dump(blob, utf8_out, indent=2) # indent=2 is for legibility while debugging - remove to save bandwidth
