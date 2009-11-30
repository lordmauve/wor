import sys
try:
	import json
except ImportError:
	try:
		import simplejson as json
	except ImportError:
		print >>sys.stderr, "simplejson is required for Python <2.6"
		print >>sys.stderr, "try easy_install simplejson or download from http://pypi.python.org/pypi/simplejson/"
		sys.exit(3)

import codecs
import datetime

from django.http import HttpResponse, Http404, HttpResponseNotAllowed
from wor.db import db

from wor.items.base import Item
from wor.world.location import Location

from Context import Context
import Util


class JSONResponse(HttpResponse):
	def __init__(self, blob):
		super(JSONResponse, self).__init__(mimetype='text/javascript; charset=UTF-8')
		utf8_out = codecs.getwriter('utf8')(self)
		json.dump(blob, utf8_out, indent=2) # indent=2 is for legibility while debugging - remove to save bandwidth


account = 'mauve'

def actors(request):
	accounts = db.accounts()
	acts = []
	for player in accounts.get_account(account).get_players():
		acts[player.id] = player.name
	return JSONResponse(acts)


def item_names(request, name=None):
	if name is None:
		return JSONResponse(dict((internal, icls.name_for()) for internal, icls in Item.list_all_classes().items()))
	else:
		return JSONResponse(Item.get_class(name).name_for())


def get_actor(request):
	"""Retrieve the current actor from the request"""
	try:
		pid = int(request.META['HTTP_X_WOR_ACTOR'])
		player = db.world().get_actor(pid)
	except KeyError:
		player = db.accounts().get_account(request.session['account']).get_players()[0]
	Context.context = player
	return player


def actor_detail(request, op, target=None):
	player = get_actor(request)

	if target is None: 
		actor = player
	else:
		actor = db.world().get_actor(pid)

	ctx = Context(player)
	if op == 'desc':
		return JSONResponse(actor.context_get(ctx))
	elif op == 'inventory':
		return JSONResponse(actor.inventory.context_get_equip(ctx))
	elif op == 'equipment':
		return JSONResponse(actor.equipment.context_get_equip(ctx))


def actor_log(request, target=None):
	player = get_actor(request)
	if target is None: 
		actor = player
	else:
		actor = db.world().get_actor(pid)

	since = 0 #request.META.get('X-WoR-Messages-Since', getattr(actor, 'last_action', 0))

	return JSONResponse(actor.get_messages(since))


def actions(request):
	player = get_actor(request)
	if request.method == 'GET':
		# List of actions
		acts = player.get_actions()
		data = [act.context_get(player.get_context()) for id, act in acts.iteritems()]
		return JSONResponse(data)
	elif request.method == 'POST':
		if 'action' in request.POST:
			player.perform_action(request.POST['action'], request.POST)

		# Save any game state that might have changed
		db.commit()
		return JSONResponse('OK')
	else:
		return HttpNotAllowed(['GET', 'POST'])


def location(request, op, location_id=None):
	player = get_actor(request)
	if location_id is None:
		location = player.loc()
	else:	
		location = Location.load(int(location_id))

	ctx = Context(player)
	if op == 'desc':
		return JSONResponse(location.context_get(ctx))
	elif op == 'actions':
		return JSONResponse(None)
	else:
		raise Http404()


def neighbourhood(request):
	player = get_actor(request)
	here = player.loc()

	sight = player.power('sight')

	ctx = Context(player)
	locs = []
	for loc in get_neighbourhood(here, sight, player):
		if loc is None or loc == 'unknown':
			locs.append(loc)
		else:
			locs.append(loc.context_get(ctx))

	return JSONResponse(locs)


def item(request, item_id):
	item = Item.load(int(item_id))
	return JSONResponse(item.context_get())


# not a view
def get_neighbourhood(here, dist, player=None):
	locs = []
	this_ring = [here]


	# For each of the other rings, we construct it using
	# information from the previous ring
	for distance in range(1, dist + 1):
		locs += this_ring
		prev_ring = this_ring
		this_ring = []

		# Each edge is essentially the same construction method
		for edge in range(0, 6):
			# For this edge of the current ring, we start with the
			# "straight-out" hex:
			dep = prev_ring[edge * (distance-1)]
			if dep == None:
				this_ring.append(None)
			else:
				loc = dep.local_directions[edge](dep, player)
				this_ring.append(loc)
				
			# Now do the remaining elements of the current ring
			for h in range(1, distance):
				prev_pos = edge * (distance - 1) + h - 1

				# This hex's antecedents
				a0 = prev_ring[prev_pos]
				a1 = prev_ring[(prev_pos + 1) % len(prev_ring)]

				# Check that neither antecedent was unknown
				if a0 == "unknown" or a1 == "unknown":
					this_ring.append("unknown")
					continue

				# Deal with the case if both antecedents are undefined
				if a0 == None and a1 == None:
					this_ring.append(None)
					continue

				# Deal with one or other antecedents being undefined
				if a0 == None:
					loc = a1.local_directions[edge](a1, player)
				elif a1 == None:
					loc = a0.local_directions[(edge + 1) % 6](a0, player)
				# or check that both paths to this hex yield the same
				# result
				elif (a1.local_directions[edge](a1, player)
					 != a0.local_directions[(edge + 1) % 6](a0, player)):
					this_ring.append("unknown")
					continue
				else:
					loc = a1.local_directions[edge](a1, player)

				this_ring.append(loc)
	return locs + this_ring
