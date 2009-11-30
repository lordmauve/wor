#!/usr/bin/python

import unittest

import Serialisation
import TestItemContainer
import TestStrategy

s = unittest.TestSuite()
s.addTest(Serialisation.suite())
s.addTest(TestItemContainer.suite())
s.addTest(TestStrategy.suite())

unittest.TextTestRunner(verbosity=2).run(s)
