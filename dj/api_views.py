from django.http import HttpResponse, Http404, HttpResponseNotAllowed
from Database import DB, retry_process

from Item import Item
from Player import Player
from Actor import Actor
from Location import Location

import Context
import GameUtil
import Util

account = 'mauve'

def actors(request):
	cur = DB.cursor()
	cur.execute("SELECT actor.id, actor.name"
				+ " FROM actor, account_actor, account"
				+ " WHERE actor.id = account_actor.actor_id"
				+ "   AND account_actor.account_id = account.account_id"
				+ "   AND account.username = %(username)s",
				{ 'username': account })

	resp = HttpResponse()
	row = cur.fetchone()
	while row != None:
		resp.write("id:%d\n" % row[0])
		resp.write("name:%s\n" % row[1])
		resp.write("-\n")
		row = cur.fetchone()
	return resp


def write_class(req, name):
	"""Get the class details for the given class (name), and render it
	back to the requester. Return True if successful."""
	try:
		cls = Item.get_class(name)
	except ImportError:
		return False

	req.write(name + ":" + cls.name_for() + "\n")

	return True


def item_names(request, name=None):
	resp = HttpResponse()
	if name is None:
		for icls in Item.list_all_classes():
			write_class(resp, icls)
	else:
		write_class(resp, name)
	return resp


def get_actor(request):
	"""Retrieve the current actor from the request"""
	try:
		pid = int(request.META['HTTP_X_WOR_ACTOR'])
	except:	
		from ui.models import Account
		account = Account.objects.get(pk=request.session['account'])
		pid = account.actors()[0].id
		
	player = Player.load(pid)
	if player is None:
		raise KeyError('Invalid player id')
	Context.context = player
	return player


def actor_detail(request, op, target=None):
	player = get_actor(request)
	Context.context = player
	if target is None: 
		actor = player
	else:
		actor = Actor.load(int(target))
	
	resp = HttpResponse()
	if op == 'desc':
		info = actor.context_get()
		Util.render_info(info, resp)
		return resp

	if op == 'inventory':
		info = actor.inventory.context_get_equip()
	elif op == 'equipment':
		info = actor.equipment.context_get_equip()
	Util.render_table(info, resp)
	return resp


def actor_log(request, target=None):
	player = get_actor(request)
	Context.context = player
	if target is None: 
		actor = player
	else:
		actor = Actor.load(int(target))

	since = request.META.get('X-WoR-Messages-Since', getattr(actor, 'last_action', 0))
		
	info = actor.get_messages(since)
	resp = HttpResponse()
	Util.render_table(info, resp)
	return resp


def actions(request):
	player = get_actor(request)
	if request.method == 'GET':
		# List of actions
		acts = player.get_actions()
		resp = HttpResponse()
		for id, act in acts.iteritems():
			info = act.context_get()
			Util.render_info(info, resp)
			resp.write("-\n")
		return resp
	elif request.method == 'POST':
		if 'action' in request.POST:
			actor.perform_action(request.POST['action'], request.POST)

		# Save any game state that might have changed
		GameUtil.save()
		return HttpResponse('OK')
	else:
		return HttpNotAllowed(['GET', 'POST'])


def neighbourhood(request):
	player = get_actor(request)
	target = player.loc()._id


def location(request, op, location_id=None):
	player = get_actor(request)
	if location_id is None:
		location = player.loc()
	else:	
		location = Location.load(int(location_id))

	resp = HttpResponse()
	if op == 'desc':
		info = location.context_get()
		Util.render_info(info, resp)
		return resp
	elif op == 'actions':
		return resp
	else:
		raise Http404()


def neighbourhood(request):
	player = get_actor(request)
	here = player.loc()

	sight = player.power('sight')

	resp = HttpResponse()
	for loc in get_neighbourhood(here, sight):
		if loc is None:
			resp.write('type:none\n-\n')
		elif loc == 'unknown':
			resp.write('type:unknown\n-\n')
		else:
			info = loc.context_get()
			Util.render_info(info, resp)
			resp.write('-\n')

	return resp


def item(request, item_id):
	item = Item.load(int(item_id))
	info = item.context_get()
	resp = HttpResponse()
	Util.render_info(info, req)
	return resp


# not a view
def get_neighbourhood(here, dist):
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
				loc = dep.local_directions[edge](dep)
				this_ring.append(loc)
				
			# Now do the remaining elements of the current ring
			for h in range(1, distance):
				prev_pos = edge*(distance-1) + h - 1

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
					loc = a1.local_directions[edge](a1)
				elif a1 == None:
					loc = a0.local_directions[(edge + 1) % 6](a0)
				# or check that both paths to this hex yield the same
				# result
				elif (a1.local_directions[edge](a1)
					 != a0.local_directions[(edge + 1) % 6](a0)):
					this_ring.append("unknown")
					continue
				else:
					loc = a1.local_directions[edge](a1)

				this_ring.append(loc)
	return locs + this_ring
