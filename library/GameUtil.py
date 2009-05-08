"""Game-level (e.g. high level) utilities"""

from Item import Item
from Player import Player

def save():
    """Save all first-class object caches"""
    Item.save_cache()
    Player.save_cache()
    #Location.save_cache()
