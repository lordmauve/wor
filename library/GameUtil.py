"""Game-level (e.g. high level) utilities"""

from Actor import Actor
from Item import Item
from Location import Location

def save():
	"""Save all first-class object caches"""
	Item.save_cache()
	Actor.save_cache()
	Location.save_cache()
