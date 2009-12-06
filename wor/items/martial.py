from base import Item


class Punch(Item):
	name = "punch"
	name_plural = "punches"
	damage = 1
	sticky = True
	group = "Weapons"


class Haymaker(Punch):
	name = "haymaker"
	name_plural = "haymakers"
	damage = 1
	sticky = True
	tohit = -40

