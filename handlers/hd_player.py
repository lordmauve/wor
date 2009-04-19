#######
# Handlers for player requests

from mod_python import apache
from Database import DB, retry_process
from Player import Player
from Logger import log
import sys
import os

public_properties = [
    '_id', 'username',
    'x',
    'y',
    'align',
    'ap', 'hp', 'maxap', 'maxhp'
    ]

def default_handler(req):
    # FIXME: Need to initialise the environment here (clear/check
    # caches, etc) and at the top of *every* handler. Possibly in a
    # separate handler method imposed for everything?

    # FIXME: Also need to wrap all this up in a retry_process.

    req.content_type = "text/plain"
    
    player = Player.load_by_name(req.user)

    log.debug("Action handler")

    if player == None:
        req.write("Null player")
        return apache.HTTP_INTERNAL_SERVER_ERROR

    log.debug("Player", player._id)

    if req.method == "GET":
        for k in public_properties:
            if k in player.__dict__:
                req.write(k + ":" + str(player[k]) + "\n")
    elif req.method == "PUT":
        # Updates?
        pass
    elif req.method == "POST":
        # Actions?
        pass

    return apache.OK

def action_handler(req):
    req.content_type = "text/plain"

    player = Player.load_by_name(req.user)

    log.debug("Action handler")

    if player == None:
        req.write("Null player")
        return apache.HTTP_INTERNAL_SERVER_ERROR

    log.debug("Player:", player._id)

    if req.method == "GET":
        acts = player.actions()
        for (id, act) in acts.items():
            if act.valid():
                req.write(act.display())
    elif req.method == "POST":
        # FIXME: Should this be handled here, or at a central point?
        # FIXME: Work out which action to handle, and do it
        pass

    return apache.OK

def inventory_handler(req):
    return apache.OK
