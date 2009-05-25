"""Web handlers for items"""

import Context
import Util
from Item import Item
from Logger import log
from mod_python import apache

def item_names_handler(req, components):
	"""Handle a request for item class information"""
	# We must have at most one component in the request URL
	if len(components) > 1:
		return apache.HTTP_NOT_FOUND

	req.content_type = "text/plain"

	# Now handle everything else: it's all GETs from here on
	if req.method != 'GET':
		# If it's not a GET, throw a wobbly
		return apache.HTTP_METHOD_NOT_ALLOWED

	log.debug("Items handler: requested " + str(components))
	if len(components) == 0:
		for icls in Item.list_all_classes():
			write_class(req, icls)
	else:
		if not write_class(req, components[0]):
			return apache.HTTP_NOT_FOUND

	return apache.OK

def write_class(req, name):
	"""Get the class details for the given class (name), and render it
	back to the requester. Return True if successful."""
	try:
		cls = Item.get_class(name)
	except ImportError:
		return False

	req.write(name + ":" + cls.name_for() + "\n")

	return True
