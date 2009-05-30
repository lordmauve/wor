#######
# Handlers for location requests

import sys
import os
from mod_python import apache
from Database import DB, retry_process
from Player import Player
from Location import Location
from Logger import log
import Util

def location_handler(req, loc, components):
	"""Handle a request for information on a single location"""
	if len(components) != 1:
		return apache.HTTP_NOT_FOUND

	if req.method != 'GET':
		return apache.HTTP_METHOD_NOT_ALLOWED

	req.content_type = "text/plain"
	here = Location.load(loc)

	if components[0] == 'desc':
		info = here.context_get()
		Util.render_info(info, req)
	elif components[0] == 'actions':
		# Return possible location-based actions
		pass
	else:
		return apache.HTTP_NOT_FOUND

	return apache.OK

def neighbourhood_handler(req, loc, components):
	"""Handle a request for the neighbourhood of this location"""
	if len(components) != 1:
		return apache.HTTP_NOT_FOUND

	if req.method != 'GET':
		return apache.HTTP_METHOD_NOT_ALLOWED
	
	req.content_type = "text/plain"
	here = Location.load(loc)

	# FIXME: When r() and friends are fixed, use them instead
	#for l in (here, here.r(), here.ur(), here.ul(), here.l(),
	#			here.ll(), here.lr()):
	for l in (here, here.e(), here.ne(), here.nw(), here.w(),
				here.sw(), here.se()):
		if l == None:
			continue
		info = l.context_get()
		Util.render_info(info, req)
		req.write('-')

	return apache.OK
