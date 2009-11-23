#!/usr/bin/python

"""Test cases for ItemContainer"""

import unittest

from TestDatabaseSetup import TestDatabaseSetup
from Alignment import Alignment
from Player import Player
from Item import Item
from Items.Rock import Rock # A non-aggregate item
from Items.GoldPiece import GoldPiece # An aggregate item
import GameUtil

class TestItemContainer(TestDatabaseSetup):
	def setUp(self):
		TestDatabaseSetup.setUp(self)
		self.p1 = Player("Vladimir", Alignment.WOOD)
		self.p2 = Player("Estragon", Alignment.METAL)
		self.rock = Rock()
		self.gp3 = GoldPiece(3)

	def testAddBasic(self):
		self.p1.inventory.add(self.rock)
		GameUtil.save()
		self.cur.execute("SELECT COUNT(*) FROM item_owner"
						 + " WHERE item_id = %(iid)s",
						 { 'iid': self.rock._id })
		row = self.cur.fetchone()
		self.assert_(row is not None)
		self.assertEqual(row[0], 1)

	def testAddAggregate(self):
		self.p1.inventory.add(self.gp3)
		GameUtil.save()
		self.cur.execute("SELECT COUNT(*) FROM item_owner"
						 + " WHERE item_id = %(iid)s",
						 { 'iid': self.gp3._id })
		row = self.cur.fetchone()
		self.assert_(row is not None)
		self.assertEqual(row[0], 1)

	def testAddAggregateToExisting(self):
		self.p1.inventory.add(self.gp3)
		gp5 = GoldPiece(5)
		self.p1.inventory.add(gp5)
		itemset = self.p1.inventory["GoldPiece"]
		item_id = iter(itemset).next()
		item = Item.load(item_id)
		self.assertEqual(item.count, 8)

	def testHasBasicPositiveOne(self):
		self.p1.inventory.add(self.rock)
		self.assert_(self.p1.inventory.has(Rock))

	def testHasBasicNegativeOne(self):
		self.p1.inventory.add(self.rock)
		self.failIf(self.p1.inventory.has(Rock, 2))

	def testHasBasicPositiveMany(self):
		self.p1.inventory.add(self.rock)
		self.p1.inventory.add(Rock())
		self.assert_(self.p1.inventory.has(Rock, 2))

	def testHasBasicNegativeMany(self):
		self.p1.inventory.add(self.rock)
		self.p1.inventory.add(Rock())
		self.failIf(self.p1.inventory.has(Rock, 3))

	def testHasAggregatePositive(self):
		self.p1.inventory.add(self.gp3)
		self.assert_(self.p1.inventory.has(GoldPiece, 2))

	def testHasAggregateNegative(self):
		self.p1.inventory.add(self.gp3)
		self.failIf(self.p1.inventory.has(GoldPiece, 10))

	def testRetrieveById(self):
		self.p1.inventory.add(self.rock)
		self.assert_(self.p1.inventory[self.rock._id] is self.rock)

	def testRetrieveByName(self):
		self.p1.inventory.add(self.rock)
		otherrock = Rock()
		self.p1.inventory.add(otherrock)
		iset = self.p1.inventory["Rock"]
		self.assertEqual(len(iset), 2)
		self.assert_(self.rock._id in iset)
		self.assert_(otherrock._id in iset)

	def testRetrieveByIdFail(self):
		try:
			i = self.p1.inventory[-1]
		except KeyError:
			self.assert_(True)
		else:
			self.fail()

	def testRetrieveByNameFail(self):
		try:
			i = self.p1.inventory["DEREK"]
		except KeyError:
			self.assert_(True)
		else:
			self.fail()

	def testRetrieveByFoo(self):
		self.p1.inventory.add(self.rock)
		try:
			i = self.p1.inventory[Rock]
		except TypeError:
			self.assert_(True)
		else:
			self.fail()

	def testContains(self):
		self.p1.inventory.add(self.rock)
		self.assert_(self.rock in self.p1.inventory)
		self.assert_(self.rock._id in self.p1.inventory)

	def testContainsFail(self):
		self.failIf(self.rock in self.p1.inventory)

	def testRemove(self):
		self.p1.inventory.add(self.rock)
		self.assert_(self.rock in self.p1.inventory)
		item = self.p1.inventory.remove(self.rock)
		self.failIf(self.rock in self.p1.inventory)
		self.assert_(item is self.rock)

def suite():
	s = unittest.TestSuite()
	s.addTest(unittest.TestLoader().loadTestsFromTestCase(TestItemContainer))
	return s

if __name__ == '__main__':
	unittest.main()
