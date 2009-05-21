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

def render_info(info, req, prefix=''):
	"""Recursively render the data in info into the request object"""
	log.debug(str(info))
	for k, v in info.iteritems():
		if isinstance(v, dict):
			render_info(v, req, prefix + k + '.')
		else:
			req.write(prefix + k + ':' + str(v).replace('\n', '\n ') + '\n')
