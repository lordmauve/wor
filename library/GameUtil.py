"""Game-level (e.g. high level) utilities"""

from Actor import Actor
from Item import Item
from Location import Location

def save():
	"""Save all first-class object caches"""
	Item.save_cache()
	Actor.save_cache()
	Location.save_cache()

def flush_cache():
	"""Flush all object caches. This function does *not* save the
	contents of the caches, or invalidate existing objects. Only use
	this function if you are holding no first-class game objects, and
	do not wish to keep any unsaved changes."""
	Actor.flush_cache()
	Item.flush_cache()
	Location.flush_cache()
