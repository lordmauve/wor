##########
# Alignment rules

class Alignment:
	WOOD = 0
	EARTH = 1
	WATER = 2
	FIRE = 3
	METAL = 4
	
	def __init__(self, align):
		self.align = align

	def beats(self, align):
		return (self.align + 1) % 5 == align.align

	def creates(self, align):
		return (self.align + 3) % 5 == align.align

	def name(self):
		return ['Wood', 'Earth', 'Water', 'Fire', 'Metal'][self.align]

	# Wood = Strength, flexibility
	# Fire = Warmth, creativity, violence
	#  Attack strength, to-hit
	# Earth = Stability, patience
	# Metal = Rigidity, persistence, strength
	#  
	# Water = Flexibility, softness, pliancy
	#  Defence, dodging
