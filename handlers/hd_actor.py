"""Web handlers for actors"""

import Context
import Util
from Player import Player
from Logger import log
from mod_python import apache

def actor_handler(req, target, components):
	"""Handle a request for actor information, for the given target ID"""
	# We must have precisely one component in the request URL
	if len(components) != 1:
		return apache.HTTP_NOT_FOUND

	req.content_type = "text/plain"
	actor = Player.load(target)

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
		Util.render_equip(info, req)
	elif components[0] == 'equipment':
		# Equipment
		info = actor.equipment.context_get_equip()
		Util.render_equip(info, req)
	elif components[0] == 'log':
		# Actor logs
		# FIXME: get the latest actor logs from the DB and return them
		pass
	else:
		return apache.HTTP_NOT_FOUND

	return apache.OK
