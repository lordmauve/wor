from django.http import Http404, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods

from wor.db import db

from wor.items.base import Item
from wor.world.location import Location
from wor.actions.base import ActionFailed
from wor.jsonutil import JSONResponse


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
    return player


def actor_detail(request, op, target=None):
    player = get_actor(request)

    if target is None: 
        actor = player
    else:
        actor = db.world().get_actor(int(target))

    if op == 'desc':
        return JSONResponse(actor.context_get(player))
    elif op == 'inventory':
        return JSONResponse(actor.inventory.context_get_equip(player))
    elif op == 'equipment':
        return JSONResponse(actor.equipment.context_get_equip(player))


def inventory(request):
    """A view of a player's own inventory."""
    player = get_actor(request)
    return JSONResponse(player.inventory.self_get_equip(player))


def actor_log(request, target=None):
    player = get_actor(request)
    if target is None: 
        actor = player
    else:
        actor = db.world().get_actor(int(target))

    since = request.GET.get('since', getattr(actor, 'last_action', 0))

    return JSONResponse(actor.get_messages(since))


@require_http_methods(['GET', 'POST'])
def actions(request):
    from wor.actions.base import ValidationError
    player = get_actor(request)
    if request.method == 'GET':
        # List of actions
        actions = player.get_actions()
        data = [act.context_get(player) for act in actions]
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
        return HttpResponseNotAllowed(['GET', 'POST'])


def location(request, op, location_id=None):
    player = get_actor(request)
    if location_id is None:
        location = player.loc()
    else:    
        location = Location.load(int(location_id))

    if op == 'desc':
        return JSONResponse(location.context_get(player))
    elif op == 'actions':
        return JSONResponse(None)
    else:
        raise Http404()


def neighbourhood(request):
    player = get_actor(request)
    here = player.loc()

    sight = player.power('sight')

    locs = []

    world = db.world()
    for loc in world.get_neighbourhood(here, sight, player):
        if loc is None or loc == 'unknown':
            locs.append(loc)
        else:
            locs.append(loc.context_get(player))

    return JSONResponse(locs)


def item(request, item_id):
    item = Item.load(int(item_id))
    return JSONResponse(item.context_get())

