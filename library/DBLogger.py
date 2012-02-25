####
# Logging to the database

from Database import DB
import Logger
from Context import log_ctx


####
# Logging specific event types to database
def log_raw_action(actid, params):
    """Log a request for an action"""
    cur = DB.cursor()

    param_pairs = map(lambda k, v: str(k) + "=" + repr(v),
                      params.iterkeys(),
                      params.iteritems())

    sql_params = { 'stamp': log_ctx.time,
                   'req': log_ctx.id,
                   'act': actid,
                   'name': actid.split('.')[2],
                   'params': param_pairs.join(' ')
                   }
    
    cur.execute("INSERT INTO log_raw_action"
                + " (stamp, request_id, action_id, action_name, parameters)"
                + " VALUES (%(stamp)s, %(req)s, %(act)s, %(name)s, %(params)s)",
                sql_params)
    Logger.log.info((header + "ACTION %(act)s %(params)s") % sql_params)

ITEM_MERGE = "merge"
ITEM_SPLIT = "split"
ITEM_ADD = "add"
ITEM_REMOVE = "remove"
ITEM_CREATE = "create"
ITEM_DESTROY = "destroy"

def log_item_event(etype, item_id, other_item=None,
                   container=None, orig_quantity=0, new_quantity=0):
    """Log an item event"""
    cur = DB.cursor()
    sql_params = { 'stamp': log_ctx.time,
                   'req': log_ctx.id,
                   'id': item_id,
                   'type': etype,
                   }

    if etype == ITEM_MERGE or etype == ITEM_SPLIT:
        sql_params['oid'] = other_item
        sql_params['orig_q'] = orig_quantity
        sql_params['new_q'] = new_quantity
        cur.execute("INSERT INTO log_item_event"
                    + " (stamp, request_id, item_id, type,"
                    + "  other_id, orig_q, new_q)"
                    + " VALUES (%(stamp)s, %(req)s, %(id)s, %(type)s,"
                    + "         %(oid)s, %(orig_q)s, %(new_q)s)",
                    sql_params)
        Logger.log.info((Logger.header + "ITEM %(type)s %(id)d with %(oid)d") % sql_params)
    elif etype == ITEM_ADD or etype == ITEM_REMOVE:
        cid = container.identity()
        sql_params['ctyp'] = cid[0]
        sql_params['cid'] = cid[1]
        sql_params['cname'] = cid[2]
        cur.execute("INSERT INTO log_item_event"
                    + " (stamp, request_id, item_id, type, "
                    + "  owner_type, owner_id, container)"
                    + " VALUES (%(stamp)s, %(req)s, %(id)s, %(type)s,"
                    + "         %(ctyp)s, %(cid)s, %(cname)s)",
                    sql_params)
        if etype == ITEM_ADD:
            sql_params['preposition'] = "into"
        else:
            sql_params['preposition'] = "from"
        Logger.log.info((Logger.header + "ITEM %(type)s %(id)d %(preposition)s %(ctyp)s/%(cid)d/%(cname)s") % sql_params)
    elif etype == ITEM_CREATE or etype == ITEM_DESTROY:
        cur.execute("INSERT INTO log_item_event"
                    + " (stamp, request_id, item_id, type)"
                    + " VALUES (%(stamp)s, %(req)s, %(id)s, %(type)s)",
                    sql_params)
        Logger.log.info((Logger.header + "ITEM %(type)s %(id)d") % sql_params)

def log_location_event():
    """Log a location event"""
    # FIXME: fill in code here
    pass

def log_actor_event():
    """Log an actor event/trigger"""
    # FIXME: fill in code here
    pass
