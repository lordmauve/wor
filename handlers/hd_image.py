#######
# Handlers for image requests

import sys
import os
import math
import traceback
from mod_python import apache

import Database # Not actually needed in this file, except to solve a
                # circular reference in "import Util"
import Logger
import Util
import Context
from ImageMaker.ImageRequest import ImageRequest

def image_handler(req):
	try:
		Context.set_request_id()
		Context.set_server_config(req.get_options())
		return image_handler_core(req)
	except apache.SERVER_RETURN, ex:
		# Catch and re-raise apache/mod_python exceptions here
		raise
	except apache.HTTP_NOT_FOUND, ex:
		raise
	except IOError, ex:
		# IOErrors in this code are generally going to be simple
		# file-not-found errors

		# Get the details of the last exception
		exlist = sys.exc_info()
		# Get a list of text lines (possibly with embedded \n)
		# describing the full backtrace
		exdata = traceback.format_exception(exlist[0], exlist[1], exlist[2])
		# Write those lines to the exception log
		head = Logger.header % { 'stamp': Context.request_time, 'req': Context.request_id }
		Logger.exception_log.error(head + ''.join(exdata))
		
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
	global meta_cache
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
	# Check that we haven't gone outside the main terrain directory
	set_path = os.path.normpath(os.path.join(Context.terrain_dir, terrain_set))
	if not ( os.path.isdir(set_path)
			 and os.path.commonprefix([ Context.terrain_dir, set_path ])
			     == Context.terrain_dir ):
		req.status = apache.HTTP_NOT_FOUND
		req.write('Image set not found')
		Logger.log.info("Image set not found: " + set_path)
		return apache.OK

	# Get metadata and metrics about the terrain set
	meta = get_meta(terrain_set)

	# Look at the requested file
	terrain_file = components.pop(0)
	if terrain_file == "metadata":
		Logger.log.debug("Returning metadata")
		Util.render_info(meta, req)
	elif terrain_file == "base":
		#  Deliver up base files (direct from the base directory?)
		pass
	else:
		image_request = ImageRequest(meta, terrain_file)
		req.sendfile(image_request.get_image())

	return apache.OK


def get_meta(image_set):
	meta_file = open(os.path.join(Context.terrain_dir,
								  image_set,
								  "metadata.txt"),
					 "r")
	meta = Util.parse_input(meta_file)
	# Remove comments
	del meta["#"]
	# Convert to integer
	for k in ("image-width", "image-height", "stride-height", "border-mask-top"):
		if k in meta:
			meta[k] = int(meta[k])
	# Compute missing geometry
	if "image-height" not in meta:
		meta["image-height"] = meta["image-width"]*4/3
	if "stride-height" not in meta:
		meta["stride-height"] = meta["image-height"]*3/4
	if "border-mask-side" not in meta:
		meta["border-mask-side"] = "%d,%d" % (
			int(meta["image-width"] * 0.086),
			int(meta["image-width"] / 20.0)
			) # 0.86 ~= sin(60)
	if "border-mask-top" not in meta:
		meta["border-mask-top"] = int(meta["image_width"] / 10.0)
	if "image-scales" not in meta:
		meta["image-scales"] = "200,100,50,25,12,6"
	# Split the acceptable scales and convert to int
	meta["image-scales"] = [ int(v) for v in meta["image-scales"].split(",") ]
	# Split the mask coordinates and convert to int
	meta["border-mask-side"] = [ int(v) for v in meta["border-mask-side"].split(",") ]

	# Add set name
	meta["image-set"] = image_set

	return meta
