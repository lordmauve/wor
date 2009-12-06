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
from wor.actions.base import ActionFailed

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

	since = request.GET.get('since', getattr(actor, 'last_action', 0))

	return JSONResponse(actor.get_messages(since))


def actions(request):
	from wor.actions.base import ValidationError
	player = get_actor(request)
	if request.method == 'GET':
		# List of actions
		actions = player.get_actions()
		data = [act.context_get(player.get_context()) for act in actions]
		return JSONResponse(data)
	elif request.method == 'POST':
		if 'action' not in request.POST:
			return JSONResponse({'error': u"No 'action' key specified"})

		try:
			message = player.perform_action(request.POST['action'], request.POST)
		except (ValidationError, ActionFailed), e:
			return JSONResponse({'error': str(e)})

		# Save any game state that might have changed
		db.commit()
		return JSONResponse({'message': message})
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

	world = db.world()
	for loc in world.get_neighbourhood(here, sight, player):
		if loc is None or loc == 'unknown':
			locs.append(loc)
		else:
			locs.append(loc.context_get(ctx))

	return JSONResponse(locs)


def item(request, item_id):
	item = Item.load(int(item_id))
	return JSONResponse(item.context_get())

