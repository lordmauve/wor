########
# Player Character

from Database import DB
import pickle
import Actor
from SimpleAction import SimpleAction
from SimpleTimedCounter import SimpleTimedCounter
from Logger import log

class Player(Actor.Actor):
    table = 'player'
    cache_by_id = {}
    cache_by_name = {}

    ####
    # Load a named instance of this object
    @staticmethod
    def _load(pid):
        player = Actor.load_actor(pid, Player.table)
        player._type = "Player"
        Player.cache_by_id[player._id] = player
        #Player.cache_by_name[player.username] = player
        return player

    @staticmethod
    def load_by_name(name):
        if name in Player.cache_by_name:
            return Player.cache_by_name[name]

        cur = DB.cursor()
        cur.execute("SELECT id FROM player WHERE username = %(name)s",
                    { 'name': name } )
        row = cur.fetchone()
        if row == None:
            return None
        log.debug("Loading player %d" % row[0])
        return Player._load(row[0])

    @staticmethod
    def load(pid):
        if pid in Player.cache_by_id:
            return Player.cache_by_id[pid]
        return _load(pid)

    def __getnewargs__(self):
        log.debug("__getnewargs__ called for player", self._id)
        self._type = "Player"

    ####
    # Create a new player
    def __init__(self, name, password, align):
        super(Player, self).__init__()
        self.align = align
        self.ap = SimpleTimedCounter(120, 360, 240) # Start at 120, maximum 240, get one more every 6 minutes (240 per day)
        self.hp = 300
        self.maxhp = 300

        cur = DB.cursor()
        cur.execute('INSERT INTO ' + self.table
                    + ' (username, password)'
                    + 'VALUES (%(username)s, %(password)s)',
                    { 'username': name,
                      'password': password }
                    )
        self._id = cur.lastrowid
        self._type = "Player"

    ####
    # Movement
    def move_to(self, pos):
        self.pos = pos

    def teleport_to(self, pos):
        self.pos = pos

    ####
    # Actions
    def actions(self):
        """Create and return a hash of all possible actions this
        player might perform"""
        acts = {}
        acts["say_boo"] = SimpleAction(self, "say_boo", cap="Say Boo", action=self.say_boo)
        
        return acts

    def say_boo(self):
        self.message("Boo!")
