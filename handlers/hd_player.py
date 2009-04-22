#######
# Handlers for player requests

from mod_python import apache, util
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

    log.debug("Default Player handler")

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
    player = Player.load_by_name(req.user)

    log.debug("Action handler")

    if player == None:
        log.debug("Null player")
        req.write("Null player")
        return apache.HTTP_INTERNAL_SERVER_ERROR

    log.debug("Player:", player._id)

    if req.method == "GET":
        req.content_type = "text/plain"
        acts = player.actions()
        for (id, act) in acts.items():
            if act.valid():
                req.write(act.display())

    elif req.method == "POST":
        # Get the content from the request
        req.form = util.FieldStorage(req)

        act = req.form.get("action", "").split(".")
        if len(act) != 3:
            # Error
            req.write("Unknown action format: " + req.form.getfirst("action"))
            return apache.HTTP_INTERNAL_SERVER_ERROR

        # Get the target of the action
        target_type = act[0]
        if target_type == "Player":
            target = Player.load(act[1])
        elif target_type == "Location":
            target = Location.load(act[1])

        # Do the action
        target.perform_action(act[2], req)

    return apache.OK

def inventory_handler(req):
    return apache.OK
