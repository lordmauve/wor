"""Web handlers for actors"""

import Context
import Util
import GameUtil
from Location import Location
from Player import Player
from Actor import Actor
from Item import Item
from Logger import log
from mod_python import apache

def actor_handler(req, target, components):
	"""Handle a request for actor information, for the given target ID"""
	# We must have precisely one component in the request URL
	if len(components) != 1:
		return apache.HTTP_NOT_FOUND

	req.content_type = "text/plain"
	actor = Actor.load(target)

	# Check for actions first -- simplifies the handling of action POSTs
	if components[0] == 'actions':
		if req.method == 'GET':
			# List of actions
			acts = actor.get_actions()
			for id, act in acts.iteritems():
				info = act.context_get()
				Util.render_info(info, req)
				req.write("-\n")

		elif req.method == 'POST':
			data = Util.parse_input(req)
			if 'action' in data:
				actor.perform_action(data['action'], data)

			# Save any game state that might have changed
			GameUtil.save()
		else:
			# If it's not GET or POST, complain
			return apache.HTTP_METHOD_NOT_ALLOWED
		
		return apache.OK

	# Now handle everything else: it's all GETs from here on
	if req.method != 'GET':
		# If it's not a GET, throw a wobbly
		return apache.HTTP_METHOD_NOT_ALLOWED

	log.debug("Actor handler: requested " + str(components))
	if components[0] == 'desc':
		# Description
		info = actor.context_get()
		Util.render_info(info, req)
	elif components[0] == 'inventory':
		# Inventory
		info = actor.inventory.context_get_equip()
		Util.render_table(info, req)
	elif components[0] == 'equipment':
		# Equipment
		info = actor.equipment.context_get_equip()
		Util.render_table(info, req)
	elif components[0] == 'log':
		# Actor logs
		if 'X-WoR-Messages-Since' in req.headers_in:
			since = req.headers_in['X-WoR-Messages-Since']
		else:
			since = getattr(actor, 'last_action', 0)
			
		info = actor.get_messages(since)
		Util.render_table(info, req)
	else:
		return apache.HTTP_NOT_FOUND

	return apache.OK
