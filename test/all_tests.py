#!/usr/bin/python

import unittest

import Serialisation

s = Serialisation.suite()

unittest.TextTestRunner(verbosity=2).run(s)
