"""An image component: A stack of images, composited together"""

import os.path
import Image

from Part import Part
import Context

class Component(Part):
	cache = "component"
	source = "fragment"
	
	def __init__(self, image_set, stack):
		super(Component, self).__init__(image_set)
		self.stack = stack

	def base_name(self):
		return '.'.join(self.stack)
