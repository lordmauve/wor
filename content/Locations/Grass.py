import time

from Location import Location
from Action import Action

class Grass(Location):
	move_ap = 2
	name = "Grasslands"
	image_name = "grass"

	def __init__(self):
		self.grass_height = 3
		self.max_height = 3
		self.growth_period = 60*60*24*7 # Grow one unit a week
		self.next_growth = time.time()

	def description(self, player):
		if self.grass_height == 3:
			return "Long flowing grasses, waving gently in the wind"
		elif self.grass_height == 2:
			return "Long flowing grasslands, with occasional bare patches"
		elif self.grass_height == 1:
			return "Thin stubbly land, with occasional tufts of grass"
		else:
			return "Grubby stubble"

	def external_actions(self, acts, player, name=None):
		Location.external_actions(acts, player, name)

		# Cut grass, if it's long enough, and the user has a scythe
		if self.grass_height > 0 and player.power("cut_grass") >= 1:
			uid = Action.make_id(self, "cut")
			acts[uid] = Action(uid, player, caption="Cut Grass",
							   ap=5, action=lambda d: self.cut_grass(player))

	def cut_grass(self, player):
		self.grass_height -= 1
		self.next_growth = time.time() + self.growth_period
		player.add_items("Grass", 1)
