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
import Context

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
	if len(components) != 0:
		return apache.HTTP_NOT_FOUND

	if req.method != 'GET':
		return apache.HTTP_METHOD_NOT_ALLOWED
	
	req.content_type = "text/plain"
	here = Location.load(loc)

	if Context.context == Context.ADMIN_CTX:
		sight = 2
	else:
		sight = Context.context.power('sight')
	
	# We construct each ring of output in turn, keeping it for the
	# next ring.
	# Start with the first "ring": the centre
	this_ring = [ here ]
	if here == None:
		req.write('type:none\n-\n')
	else:
		info = here.context_get()
		Util.render_info(info, req)
		req.write('-\n')

	# For each of the other rings, we construct it using
	# information from the previous ring
	for distance in range(1, sight+1):
		prev_ring = this_ring
		this_ring = []
		# Each edge is essentially the same construction method
		for edge in range(0, 6):
			# For this edge of the current ring, we start with the
			# "straight-out" hex:
			dep = prev_ring[edge * (distance-1)]
			if dep == None:
				this_ring.append(None)
				req.write('type:none\n')
			else:
				loc = dep.local_directions[edge](dep)
				this_ring.append(loc)
				if loc == None:
					req.write('type:none\n')
				else:
					info = loc.context_get()
					Util.render_info(info, req)
				
			req.write('-\n')

			# Now do the remaining elements of the current ring
			for h in range(1, distance):
				prev_pos = edge*(distance-1) + h - 1
				# This hex's antecedents
				a0 = prev_ring[prev_pos]
				a1 = prev_ring[(prev_pos+1)%len(prev_ring)]
				# Check that neither antecedent was unknown
				if a0 == "unknown" or a1 == "unknown":
					this_ring.append("unknown")
					req.write('type:unknown\n-\n')
					continue

				# Deal with the case if both antecedents are undefined
				if a0 == None and a1 == None:
					this_ring.append(None)
					req.write('type:none\n-\n')
					continue

				# Deal with one or other antecedents being undefined
				if a0 == None:
					loc = a1.local_directions[edge](a1)
				elif a1 == None:
					loc = a0.local_directions[(edge+1)%6](a0)
				# or check that both paths to this hex yield the same
				# result
				elif ( a1.local_directions[edge](a1)
					 != a0.local_directions[(edge+1)%6](a0) ):
					this_ring.append("unknown")
					req.write('type:unknown\n-\n')
					continue
				else:
					loc = a1.local_directions[edge](a1)

				this_ring.append(loc)
				if loc == None:
					req.write('type:none\n')
				else:
					info = loc.context_get()
					Util.render_info(info, req)

				req.write('-\n')

	return apache.OK
