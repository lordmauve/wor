########
# Player Character

from Database import DB
import pickle
import Actor
from SimpleAction import SimpleAction
from SimpleTimedCounter import SimpleTimedCounter

class Player(Actor.Actor):
    table = 'player'
    cache_by_id = {}
    cache_by_name = {}

    ####
    # Load a named instance of this object
    @staticmethod
    def _load(pid):
        player = Actor.load_actor(pid, Player.table)
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
        return Player._load(row[0])

    @staticmethod
    def load(pid):
        if pid in Player.cache_by_id:
            return Player.cache_by_id[pid]
        return _load(pid)

    def __getnewargs__(self):
        self._type = "Player"

    ####
    # Create a new player
    def __init__(self, id, password, align):
        super(Player, self).__init__(id)
        self.align = align
        self.ap = SimpleTimedCounter(120, 360, 240) # Start at 120, maximum 240, get one more every 6 minutes (240 per day)
        self.hp = 300
        self.maxhp = 300

        cur = DB.cursor()
        cur.execute('INSERT INTO ' + self.table
                    + ' (username, password)'
                    + 'VALUES (%(name)s, )',
                    { 'username': name }
                    )
        self._id = cur.lastrowid


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
