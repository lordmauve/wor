from base import Item


class Punch(Item):
	name = "punch"
	plural = "punches"
	damage = 1
	sticky = True
	group = "Weapons"


class Haymaker(Punch):
	name = "haymaker"
	plural = "haymakers"
	damage = 1
	sticky = True
	tohit = -40

