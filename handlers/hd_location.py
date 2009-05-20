#######
# Handlers for location requests

from mod_python import apache
from Database import DB, retry_process
from Player import Player
from Logger import log
import sys
import os

public_properties = [
    '_id'
    ]

def neighbourhood_handler(req):
    # FIXME: Need to initialise the environment here (clear/check
    # caches, etc) and at the top of *every* handler. Possibly in a
    # separate handler method imposed for everything?

    # FIXME: Also need to wrap all this up in a retry_process.

    req.content_type = "text/plain"
    
    player = Player.load_by_name(req.user)

    log.debug("Neighbourhood handler")

    if player == None:
        req.write("Null player")
        return apache.HTTP_INTERNAL_SERVER_ERROR

    log.debug("Player", player._id)

    if req.method == "GET":
        here = player.loc()
        for loc in (here.r(), here.ur(), here.ul(),
                    here.l(), here.ll(), here.lr()):
            for k in public_properties:
                if k in loc.__dict__:
                    req.write(k + ":" + str(loc[k]) + "\n")

    return apache.OK
