"""Fragment class for a component of a hex body: centre, and four edge
pieces"""

import os.path
import Image
import ImageDraw

from Part import Part
from ImageFragment import ImageFragment

class HexFragment(ImageFragment):
	header = "hex"

	def __init__(self, meta, image, part):
		super(HexFragment, self).__init__(meta, image)
		self.part = part

	def _make_part(self, component_name):
		"""Take a full terrain image tile and fragment it into the five
		pieces we can construct rendered images from""" 
		if (self.image != '' and self.image != None):
			im = Image.open(self._source_path(self.image))
			center_x=int(im.size[0]/2)
			top_fold=int(im.size[1]/4)
			bottom_fold=int(im.size[1]*.75)
			
			base_name = self.header + "_" + self.image + "_"

			UL=im.crop((0,0,center_x,top_fold))
			UL.save(self._cache_path(base_name + "UL"))
			UR=im.crop((center_x,0,im.size[0],top_fold))
			UR.save(self._cache_path(base_name + "UR"))
			middle=im.crop((0,top_fold,im.size[0],bottom_fold))
			middle.save(self._cache_path(base_name + "M"))
			LL=im.crop((0,bottom_fold,center_x,im.size[1]))
			LL.save(self._cache_path(base_name + "LL"))
			LR=im.crop((center_x,bottom_fold,im.size[0],im.size[1]))
			LR.save(self._cache_path(base_name + "LR"))
		else:
			# Blank string==boring, transparent image, suitable for
			# edge hexes that have nothing beyond them.  Generate it
			# if it doesn't exist yet.
			im = Image.new("LA", (1, 1), (128, 255))
			im.save(self._cache_path(self.header + "__UL"))
			im.save(self._cache_path(self.header + "__UR"))
			im.save(self._cache_path(self.header + "__M"))
			im.save(self._cache_path(self.header + "__LL"))
			im.save(self._cache_path(self.header + "__LR"))

		return Image.open(
			self._cache_path(
				self.header
				+ "_" + self.image
				+ "_" + Part.NAMES[self.part]
				)
			)
