#!/usr/bin/python

"""Basic testing for Strategy infrastructure."""

import unittest

from Strategy import Strategy, override
from Strategied import Strategied


class Base(Strategied):
	def __init__(self, v):
		self.value = v
		Strategied.__init__(self)

	def method_A(self, param1, param2):
		return self.value + param1 + param2


class TestStrat1(Strategy):
	@staticmethod
	def applied(me):
		me.strat1_applied = True

	@staticmethod
	def removed(me):
		me.strat1_applied = False

	@override
	def method_A(me, param1, param2, next_function):
		return me.value + (param1 * param2)


class TestStrat2(Strategy):
	@override
	def method_A(me, param1, param2, next_function):
		return me.value + param1 + param2 + 1


class TestStrat3(Strategy):
	@override
	def method_A(me, param1, param2, next_function):
		return next_function(me, param1, param2) + 1


class TestStrat4(Strategy):
	@override
	def method_A(me, param1, param2, next_function):
		return next_function(me, param1, param2) * 17


class TestStrategy(unittest.TestCase):
	def setUp(self):
		self.b = Base(3)

	def testBase(self):
		self.assertEqual(self.b.method_A(4, 5), 12)

	def testApplied(self):
		self.b.set_strategy("derek", TestStrat1())
		self.assert_(hasattr(self.b, "strat1_applied"))
 		self.assert_(self.b.strat1_applied)

	def testUnapplied(self):
		self.b.set_strategy("derek", TestStrat1())
		self.b.set_strategy("derek", None)
		self.assert_(hasattr(self.b, "strat1_applied"))
		self.failIf(self.b.strat1_applied)

	def testSimpleOverride(self):
		self.b.set_strategy("derek", TestStrat1())
		self.assertEqual(self.b.method_A(4, 5), 23)

	def testSimpleRemoval(self):
		self.b.set_strategy("derek", TestStrat1())
		self.b.set_strategy("derek", None)
		self.assertEqual(self.b.method_A(4, 5), 12)

	def testSimpleReplacement(self):
		self.b.set_strategy("derek", TestStrat1())
		self.b.set_strategy("derek", TestStrat2())
		self.assertEqual(self.b.method_A(4, 5), 13)

	def testSimpleReplacementAndRemoval(self):
		self.b.set_strategy("derek", TestStrat1())
		self.b.set_strategy("derek", TestStrat2())
		self.b.set_strategy("derek", None)
		self.assertEqual(self.b.method_A(4, 5), 12)

	def testComplexRemovalNoChain(self):
		self.b.set_strategy("derek", TestStrat1())
		self.b.set_strategy("clive", TestStrat2())
		self.b.set_strategy("derek", None)
		self.assertEqual(self.b.method_A(4, 5), 13)

	def testChainingOne(self):
		self.b.set_strategy("derek", TestStrat3())
		self.assertEqual(self.b.method_A(4, 5), 13)

	def testChainingMultiple(self):
		self.b.set_strategy("derek", TestStrat3())
		self.b.set_strategy("clive", TestStrat4())
		self.assertEqual(self.b.method_A(4, 5), 13*17)

	def testRemovalWithChaining(self):
		self.b.set_strategy("derek", TestStrat3())
		self.b.set_strategy("clive", TestStrat4())
		self.b.set_strategy("derek", None)
		self.assertEqual(self.b.method_A(4, 5), 12*17)


def suite():
	s = unittest.TestSuite()
	s.addTest(unittest.TestLoader().loadTestsFromTestCase(TestStrategy))
	return s

if __name__ == '__main__':
	unittest.TextTestRunner(verbosity=2).run(suite())
