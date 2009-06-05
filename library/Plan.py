"""Plan: A plan for constructing stuff from other stuff"""

plans = []

def makeable_plans(who, item):
	"""Return the list of all plans that can be made right now by who
	from item."""
	rv = []
	for p in plans:
		if item not in p.materials:
			continue
		if item not in p.catalyst:
			continue
		if p.can_be_made(who, 1):
			rv.append(p)
	return rv

def visible_plans(who):
	"""Return the list of all plans that could be made by who, if they
	had the materials"""
	rv = []
	for p in plans:
		# FIXME: Test whether the player has the appropriate alignment
		# skills
		if p.precondition(who):
			rv.append(p)
	return rv

class Plan(object):
	def __init__(self, materials, makes, ap, ap10=None,
				 align=None, catalyst={},
				 precondition=lambda p, a, q: True,
				 success=lambda p, a, q: True,
				 postcondition=lambda p, a, q: True):
		self.materials = materials
		self.makes = makes
		self.ap = ap
		self.ap10 = ap10
		if self.ap10 == None:
			self.ap10 = 10*self.ap
		self.align = align
		self.catalyst = catalyst
		self.precondition = precondition
		self.success = success
		self.postcondition = postcondition

	def can_be_made(self, who, total):
		"""Test whether who can make this recipe"""
		# FIXME: test whether the player has the appropriate alignment
		# skills		
		total = int(total)
		for iname, quant in self.materials.iteritems():
			if not who.has(iname, quant*total):
				return False

		for iname, quant in self.catalyst.iteritems():
			if not who.has(iname, quant*total):
				return False

		return self.precondition(self, who, total)

	def make(self, who, total):
		"""Make something"""
		total = int(total)
		# Test that we can actually make it
		if not self.can_be_made(who, total):
			return False

		# Take the AP
		# See http://worldofrodney.org/index.php/Dev:Low-level_Infrastructure#Build_system
		benefit10 = self.ap10 / (10 * self.ap)
		benefit_all = math.pow(benefit10, math.log10(total))
		who.ap -= math.floor(total * self.ap * benefit_all)

		# Take the materials
		for iname, quant in self.materials.iteritems():
			who.take_item(iname, quant*total)

		# Test for success, and potentially fail here
		if not self.success(self, who, total):
			return False

		# Add the results
		for iname, quant in self.makes.iteritems():
			who.add_item(iname, quant*total)
		
		# Run the postcondition
		return self.postcondition(self, who, total)
		