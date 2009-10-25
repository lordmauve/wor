"""A stack of edge bits composited together"""

import os.path
import Image

from Component import Component
from EdgeFragment import EdgeFragment

class EdgeComponent(Component):
	header = "edge"
	
	def __init__(self, image_set, stack, part):
		super(EdgeComponent, self).__init__(image_set, stack)
		self.part = part

	def _make_part(self, component_name):
		# Get the fragments we need to put ourself together
		fragments = [ EdgeFragment(self.set, name, self.part)
			      for name in self.stack ]

		# Get the base image size we should be using from the first
		# image fragment
		size = fragments[0].get_image().size
		
		# Create a base image
		base = Image.new("RGBA", size)

		# Composite each image into it
		for frag in fragments:
			base = frag.composite(base)

		# Save the image to the cache
		base.save(component_name)
		
		return base
