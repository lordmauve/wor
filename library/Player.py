########
# Player Character

from Database import DB
import Actor
from SimpleAction import SimpleAction
from SimpleTimedCounter import SimpleTimedCounter
from Logger import log

class Player(Actor.Actor):
    _table = 'player'
    cache_by_id = {}
    cache_by_name = {}

    ####
    # Load an instance of this object
    @staticmethod
    def load(pid, allprops=False):
        """Implement caching for loading a player by ID"""
        if pid in Player.cache_by_id:
            return Player.cache_by_id[pid]
        return Player._load(pid, all)

    @staticmethod
    def load_by_name(name, allprops=False):
        """Additional function to load a player by name instead of by
        ID"""
        if name in Player.cache_by_name:
            return Player.cache_by_name[name]

        cur = DB.cursor()
        cur.execute("SELECT id FROM player WHERE username = %(name)s",
                    { 'name': name } )
        row = cur.fetchone()
        if row == None:
            return None
        #log.debug("Loading player %s (=%d)" % (name, row[0]))
        return Player._load(row[0], allprops)

    @staticmethod
    def _load(pid, allprops):
        """Internal function used in loading a player -- called by
        both load() and load_by_name()"""
        player = Player.load_object(pid, Player._table, allprops)
        Player.cache_by_id[player._id] = player
        Player.cache_by_name[player.name] = player
        player._on_load()
        return player

    ####
    # Additional indices to write to the database on save
    def _save_indices(self):
        return { 'username': self.name }

    ####
    # Called on unpickling -- i.e. on load
    def _on_load(self):
        self._type = "Player"

    ####
    # Create a new player
    def __init__(self, name, password, align):
        super(Player, self).__init__()
        self.align = align
        # Start at 120AP, get one more every 6 minutes (240 per day),
        # maximum 240.
        # FIXME: Add "actor" and "power" values to this class
        self.ap = SimpleTimedCounter(self, 120, 360, 240)
        self.hp = 300
        self.maxhp = 300
        self.onload_list = [ self.ap ]
        self.name = name

        print "New ID =", self._id

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

    def say_boo(self, parent):
        log.info("Boo!")
