#######
# Handlers for image requests

import sys
import os
import math
import traceback
from mod_python import apache

import Context
from Database import DB
import Logger
from ImageMaker.ImageRequest import ImageRequest

# First shot at a handler will only take on the
# <server>/img/terrain/fileset/thingy.png requests
def image_handler(req):
	try:
		Context.set_request_id()
		Context.set_server_config(req.get_options())
		return image_handler_core(req)
	except apache.SERVER_RETURN, ex:
		# Catch and re-raise apache/mod_python exceptions here
		raise
	except IOError, ex:
		# IOErrors in this code are generally going to be simple
		# file-not-found errors
		return apache.HTTP_NOT_FOUND
	except Exception, ex:
		# Catch any other exception

		# Set up a simple Infernal Server Error response 
		req.status = apache.HTTP_INTERNAL_SERVER_ERROR
		req.write("There was an infernal server error. Please report this (with reference %s) to the admins.\n" % (Context.request_id))

		# Get the details of the last exception
		exlist = sys.exc_info()
		# Get a list of text lines (possibly with embedded \n)
		# describing the full backtrace
		exdata = traceback.format_exception(exlist[0], exlist[1], exlist[2])
		# Write those lines to the exception log
		head = Logger.header % { 'stamp': Context.request_time, 'req': Context.request_id }
		Logger.exception_log.error(head + ''.join(exdata))

		# Return the Infernal Server Error
		return apache.OK

def image_handler_core(req):
	components = req.uri.split('/')
	Logger.log.debug('image_handler entered: URL components:' + str(components) + '  Terrain dir:' + Context.terrain_dir)
	if components.pop(0) != '':
		# No leading slash -- something's screwy
		req.status = apache.HTTP_INTERNAL_SERVER_ERROR
		req.write("No leading slash on request for URL '"+req.uri+"'")
		return apache.OK

	if components.pop(0) != 'img':
		req.status = apache.HTTP_INTERNAL_SERVER_ERROR
		req.write("Incorrect path prefix on request for URL '"+req.uri+"'")
		return apache.OK
		
	if components.pop(0) != 'terrain':
		req.status = apache.HTTP_NOT_FOUND
		req.write('Image: image group not handled')
		return apache.OK

	# Get and check the existence of the terrain set
	terrain_set = components.pop(0)
	terrain_file = components.pop(0)
	image_request = ImageRequest(terrain_set, terrain_file)
	req.sendfile(image_request.get_image())
	return apache.OK
