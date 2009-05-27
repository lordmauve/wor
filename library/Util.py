####
# Simple utilities

from Logger import log

def default(v, d=0):
	"""If v is defined, return v. Otherwise, return d."""
	try:
		if v != None:
			return v
		return d
	except AttributeError:
		return d

def render_info(info, req, prefix='', indent=0):
	"""Recursively render the data in info into the request object"""
	log.debug(str(info))
	for k, v in info.iteritems():
		if isinstance(v, dict):
			render_info(v, req, prefix + k + '.', indent-len(prefix))
		else:
			fmt = "%-" + str(indent+1) + "s%s\n"
			key = prefix + k + ':'
			value = str(v).replace('\n', '\n ')
			req.write(fmt % (key, value))

def render_equip(info, req):
	"""Render a table of data in info into the request object"""
	for item in info:
		req.write(item[0] + ":" + str(item[1]) + ":" + item[2] + "\n")

def info_key_length(info):
	"""Get the maximum key length of the given info dictionary"""
	length = 0
	for k, v in info.iteritems():
		if isinstance(v, dict):
			length = max(length, len(k)+1+info_key_length(v))
		else:
			length =max(length, len(k))
	return length
