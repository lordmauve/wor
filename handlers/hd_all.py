"""Core handlers for all REST API calls. These handlers are called for
all requests, and despatch those requests to appropriate other
handlers further down the URL tree."""

from mod_python import apache

from Database import DB, retry_process
from Player import Player
from Location import Location
from Item import Item
import Context
import Logger
import hd_actor

def api_handler(req):
	"""This is the core function for the REST API. All requests pass
	through this function. It sets up the global AuthZ context for
	this request, parses the URL of the request and checks it for
	sanity, and then calls a suitable handler for it.

	When we reach this function, we have already checked
	authentication, so this is partly an authorisation handler."""
	req.get_basic_auth_pw() # Get the username as well
	account = req.user
	
	components = req.uri.split('/')
	if components[0] != '':
		# The request didn't even have a leading slash -- something's
		# screwy
		req.write("No leading slash on request for URL '"+req.uri+"'")
		return apache.HTTP_INTERNAL_SERVER_ERROR
	
	components.pop(0)
	if components[0] != 'api':
		req.write("Incorrect path prefix on request for URL '"+req.uri+"'")
		return apache.HTTP_INTERNAL_SERVER_ERROR
	components.pop(0)
		
	Logger.log.debug(str(components))
	if components[0] == '':
		apache.redirect(req, 'http://worldofrodney.org/')
		# Does not return
	elif components[0] == 'actors':
		# Get the list of actors owned by this account
		# FIXME
		pass
	else:
		act_id = check_actor(req)
		Context.context = Player.load(act_id)
		
		if components[0] == 'actor':
			if components[1] == 'self':
				# We're using self: id is actor
				target = act_id
			elif components[1].isdigit():
				target = int(components[1])
			else:
				req.write("Actor: actor not found")
				req.write(str(components))
				return apache.HTTP_NOT_FOUND

			retry_process(
				lambda: hd_actor.actor_handler(
					req,
					target,
					components[2:]))
			
		elif components[0] == 'location':
			if components[1] == 'here':
				target = Context.context.loc()._id
			elif components[1] == 'neighbourhood':
				target = Context.context.loc()._id
				DB.retry_process(
					lambda: hd_location.neighbourhood_handler(
						req,
						target, components[2:]))
				
				return apache.OK
			elif components[1].isdigit():
				target = int(components[1])
			else:
				return apache.HTTP_NOT_FOUND

			retry_process(
				lambda: hd_location.location_handler(
					req,
					target,
					components[2:]))
			
		elif components[0] == 'item':
			if components[1].isdigit():
				target = int(components[1])
			else:
				return apache.HTTP_NOT_FOUND
			
			retry_process(
				lambda: hd_item.item_handler(
					req,
					target,
					components[2:]))
		else:
			# It's not one of our expected URIs
			return apache.HTTP_NOT_FOUND

	return apache.OK

def check_actor(req, fail=True):
	"""Returns the actor ID for this request. If fail is True, and no
	actor header was provided, throw an Apache error code."""
	actor = req.headers_in['X-WoR-Actor']
	if actor is list:
		actor = actor[0]
		
	if actor == None:
		# No X-WoR-Actor header defined: return 403 if asked
		if fail:
			req.write("No actor defined\nCheck your headers\n\n")
			raise apache.SERVER_RETURN, apache.HTTP_FORBIDDEN
		else:
			return None
		
	if not actor.isdigit():
		# X-WoR-Actor header wasn't numeric: This is always an error
		req.write("Malformed actor ID\nCheck your headers\n\n")
		raise apache.SERVER_RETURN, apache.HTTP_FORBIDDEN

	return int(actor)

def cleanup_handler(req):
	"""Called at the end of every request. In this case, simply
	flushes all the caches."""
	Player.flush_cache()
	Location.flush_cache()
	Item.flush_cache()
	return apache.OK