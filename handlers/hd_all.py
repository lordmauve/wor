"""Core handlers for all REST API calls. These handlers are called for
all requests, and despatch those requests to appropriate other
handlers further down the URL tree."""

from mod_python import apache

from Database import DB, retry_process
from Player import Player
from Location import Location
from Item import Item
from Actor import Actor
import Context
import Logger
import hd_actor
import hd_item
import hd_location

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
		req.status = apache.HTTP_INTERNAL_SERVER_ERROR
		req.write("No leading slash on request for URL '"+req.uri+"'")
		return apache.OK
	
	components.pop(0)
	if components[0] != 'api':
		req.status = apache.HTTP_INTERNAL_SERVER_ERROR
		req.write("Incorrect path prefix on request for URL '"+req.uri+"'")
		return apache.OK
	components.pop(0)

	# We need to set up the logging/request context here
	Context.set_request_id()

	Logger.log.debug("Request components: " + str(components))
	if components[0] == '':
		apache.redirect(req, 'http://worldofrodney.org/')
		# Does not return
	elif components[0] == 'actors':
		# Get the list of actors owned by this account
		req.content_type = "text/plain"

		cur = DB.cursor()
		cur.execute("SELECT actor.id, actor.name"
					+ " FROM actor, account_actor, account"
					+ " WHERE actor.id = account_actor.actor_id"
					+ "   AND account_actor.account_id = account.account_id"
					+ "   AND account.username = %(username)s",
					{ 'username': account })
		row = cur.fetchone()
		while row != None:
			req.write("id:%d\n" % row[0])
			req.write("name:%s\n" % row[1])
			req.write("-\n")
			row = cur.fetchone()

		return apache.OK
			
	elif components[0] == 'items':
		# Get information on items: class/name mapping, for example
		# FIXME: Pass off to item handlers
		if components[1] == 'names':
			return retry_process(
				lambda: hd_item.item_names_handler(
					req, components[2:]))
		else:
			return apache.HTTP_NOT_FOUND
	else:
		act_id = check_actor(req)
		Context.context = Player.load(act_id)
		if Context.context == None:
			req.status = apache.HTTP_FORBIDDEN
			req.write("No context found for actor id " + str(act_id))
			return apache.OK
		
		if components[0] == 'actor':
			if components[1] == 'self':
				# We're using self: id is actor
				target = act_id
			elif components[1].isdigit():
				target = int(components[1])
			else:
				req.status = apache.HTTP_NOT_FOUND
				req.write("Actor: actor not found")
				req.write(str(components))
				return apache.OK

			return retry_process(
				lambda: hd_actor.actor_handler(
					req,
					target,
					components[2:]))
			
		elif components[0] == 'location':
			if components[1] == 'here':
				target = Context.context.loc()._id
			elif components[1] == 'neighbourhood':
				target = Context.context.loc()._id
				retry_process(
					lambda: hd_location.neighbourhood_handler(
						req,
						target, components[2:]))
				
				return apache.OK
			elif components[1].isdigit():
				target = int(components[1])
			else:
				req.status = apache.HTTP_NOT_FOUND
				req.write("Location: location not found")
				return apache.OK

			return retry_process(
				lambda: hd_location.location_handler(
					req,
					target,
					components[2:]))
			
		elif components[0] == 'item':
			if components[1].isdigit():
				target = int(components[1])
			else:
				req.status = apache.HTTP_NOT_FOUND
				req.write("Item: item not found")
				return apache.OK
			
			return retry_process(
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
	Actor.flush_cache()
	#Location.flush_cache()
	#Item.flush_cache()
	return apache.OK
