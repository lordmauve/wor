#!/usr/bin/python

import unittest

import Serialisation
import TestItemContainer

s = unittest.TestSuite()
s.addTest(Serialisation.suite())
s.addTest(TestItemContainer.suite())

unittest.TextTestRunner(verbosity=2).run(s)
