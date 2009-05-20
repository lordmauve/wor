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
		raise apache.SERVER_RETURN, apache.HTTP_NOT_FOUND

	req.content_type = "text/plain"
	actor = Player.load(target)

	# Check for actions first -- simplifies the handling of action POSTs
	if components[0] == 'actions':
		if req.method == 'GET':
			# List of actions
			acts = actor.actions()
			for (id, act) in acts.items():
				if act.valid():
					req.write(act.display())
		elif req.method == 'POST':
			# FIXME: Despatch actions here
			pass
		
		return apache.OK

	# Now handle everything else: it's all GETs from here on
	if req.method != 'GET':
		# FIXME: Throw a wobbly
		pass
		#raise apache.SERVER_RETURN, apache.

	log.debug("Actor handler: requested " + str(components))
	if components[0] == 'desc':
		# Description
		info = actor.context_get()
		Util.render_info(info, req)
	elif components[0] == 'inventory':
		# Inventory
		info = actor.inventory.context_get()
		Util.render_info(info, req)
	elif components[0] == 'equipment':
		# Equipment
		info = actor.equipment.context_get()
		Util.render_info(info, req)
	elif components[0] == 'log':
		# Actor logs
		# FIXME: get the latest actor logs from the DB and return them
		pass
	else:
		raise apache.SERVER_RETURN, apache.HTTP_NOT_FOUND

	return apache.OK
