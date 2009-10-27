"""An image component: A stack of images, composited together"""

import os.path
import Image

from Part import Part
import Context

class Component(Part):
	cache = "component"
	source = "fragment"
	
	def __init__(self, meta, stack):
		super(Component, self).__init__(meta)
		self.stack = stack

	def base_name(self):
		return '.'.join(self.stack)
