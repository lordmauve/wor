import traceback

from mod_python import apache

import Context
import Logger


def server_error(req):
	"""Handle an exception"""
	# Set up a simple Infernal Server Error response
	req.status = apache.HTTP_INTERNAL_SERVER_ERROR
	req.write("There was an infernal server error. Please report this (with reference %s) to the admins.\n" % (Context.log_ctx.id))

	# Get a list of text lines (possibly with embedded \n)
	# describing the full backtrace
	exdata = traceback.format_exc()

	# Write those lines to the exception log
	Logger.exception_log.error(exdata)

	# Return the Infernal Server Error
	return apache.HTTP_INTERNAL_SERVER_ERROR
