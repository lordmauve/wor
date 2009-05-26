########
# Player Character

from Database import DB
import Actor
from ItemContainer import ItemContainer
from Punch import Punch
from SimpleAction import SimpleAction
from SimpleTimedCounter import SimpleTimedCounter
from Position import Position
from Logger import log

class Player(Actor.Actor):
	# Additional caching over and above the cache by ID for actors
	cache_by_name = {}

	####
	# Load an instance of this object
	@classmethod
	def load_by_name(cls, name, allprops=False):
		"""Additional function to load a player by name instead of by
		ID"""
		if name in cls.cache_by_name:
			return cls.cache_by_name[name]

		cur = DB.cursor()
		cur.execute("SELECT id FROM " + cls._table
					+ " WHERE name = %(name)s",
					{ 'name': name } )
		row = cur.fetchone()
		if row == None:
			return None
		#log.debug("Loading player %s (=%d)" % (name, row[0]))
		return cls.load(row[0], allprops)

	@classmethod
	def _cache_object(cls, obj):
		"""Hook to allow classes to define their own caching scheme.
		Called after an object has been loaded and cached in
		cls.cache_by_id"""
		super(Player, cls)._cache_object(obj)
		cls.cache_by_name[obj.name] = obj

	####
	# Additional indices to write to the database on save
	def _save_indices(self):
		inds = super(Player, self)._save_indices()
		inds['name'] = self.name
		return inds

	####
	# Create a new player
	def __init__(self, name, align, position=None):
		if position == None:
			# FIXME: Make this alignment-dependent
			position = Position(0, 0, 'main')

		super(Player, self).__init__(name, position)
		self.align = align
		# Start at 120AP, get one more every 6 minutes (240 per day),
		# maximum 240.
		# FIXME: Add "actor" and "power" values to this class
		self.ap = SimpleTimedCounter(self, 120, 360, 240)
		self.hp = 300
		self.maxhp = 300
		self.inventory = ItemContainer(self, "inventory")
		punch = Punch()
		self.inventory.add(punch)

		self._cache_object(self) # Must be called explicitly in
                                 # __init__() here.

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
