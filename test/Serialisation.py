"""Test cases verifying basic creation, destruction, and serialisation
of objects in the database"""

import unittest

from TestDatabaseSetup import TestDatabaseSetup
from Alignment import Alignment
from Player import Player
from Location import Location
from Position import Position
from Items.Rock import Rock
import GameUtil

class TestCreateObjects(TestDatabaseSetup):
	def testPlayer(self):
		p = Player("test player", Alignment.WOOD)
		GameUtil.save()
		self.cur.execute("SELECT COUNT(*) FROM actor WHERE name = %(name)s",
						 { 'name': "test player" })
		row = self.cur.fetchone()
		self.assert_(row is not None)
		self.assertEqual(row[0], 1)

	def testLocation(self):
		p = Location(Position(5, -3, "test"))
		GameUtil.save()
		self.cur.execute("SELECT COUNT(*) FROM location "
						 + " WHERE x = %(x)s AND y = %(y)s AND layer = %(layer)s",
						 { 'x': 5, 'y': -3, 'layer': 'test' })
		row = self.cur.fetchone()
		self.assert_(row is not None)
		self.assertEqual(row[0], 1)
		
	def testItem(self):
		p = Rock()
		GameUtil.save()
		self.cur.execute("SELECT COUNT(*) FROM item")
		row = self.cur.fetchone()
		self.assert_(row is not None)
		self.assertEqual(row[0], 1)

class TestDestroyObjects(TestDatabaseSetup):
	def testItem(self):
		p = Rock()
		GameUtil.save()
		p.destroy()
		GameUtil.save()
		self.cur.execute("SELECT COUNT(*) FROM item")
		row = self.cur.fetchone()
		self.assert_(row is not None)
		self.assertEqual(row[0], 0)

def suite():
	s = unittest.TestSuite()
	s.addTest(unittest.TestLoader().loadTestsFromTestCase(TestCreateObjects))
	s.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDestroyObjects))
	return s

if __name__ == '__main__':
	unittest.main()
