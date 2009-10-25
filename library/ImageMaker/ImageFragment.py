"""Base class for all kinds of image fragment. Supports on-demand
fragmentation of underlying parts"""

import os.path
import Image

from Part import Part
import Context

class ImageFragment(Part):
	cache = "fragment"
	source = "base"
	
	def __init__(self, image_set, image):
		super(ImageFragment, self).__init__(image_set)
		self.image = image

	def base_name(self):
		return self.image
