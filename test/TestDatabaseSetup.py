"""Base test class for setting up a clean database"""

import sys
import os.path
# Hack up sys.path so that we can replace DBAuth for test purposes
if sys.path[0] == "":
	sys.path[1:1] = ["test",]
else:
	sys.path[1:1] = [os.path.normpath(os.path.join(sys.path[0], "..", "test")),]

from unittest import TestCase
import psycopg2

from Database import DB
import GameUtil


class TestDatabaseSetup(TestCase):
	"""Base class for all WoR unit tests: Start with a clean database
	and a clear cache."""
	def setUp(self):
		GameUtil.flush_cache()
		self.cur = DB.cursor()
		self.cur.execute("DELETE FROM account")
		self.cur.execute("DELETE FROM account_actor")
		self.cur.execute("DELETE FROM actor")
		self.cur.execute("DELETE FROM actor_message")
		self.cur.execute("DELETE FROM actor_properties")
		self.cur.execute("DELETE FROM item")
		self.cur.execute("DELETE FROM item_owner")
		self.cur.execute("DELETE FROM item_properties")
		self.cur.execute("DELETE FROM location")
		self.cur.execute("DELETE FROM location_properties")
		self.cur.execute("DELETE FROM log_raw_action")
		DB.commit()
