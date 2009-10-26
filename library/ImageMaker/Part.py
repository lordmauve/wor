"""Base for all image parts"""

import os.path
import Image

import Logger
import Context

class Part(object):
	header = None  # Prefix used on files that this type creates
	cache = None   # Directory name for the destination files
	source = None  # Directory name for the source files

	CENTRE  = 0
	HEX_UR = 1
	HEX_UL = 2
	HEX_LL = 3
	HEX_LR = 4
	EDGE_L = 5
	EDGE_R = 6
	EDGE_F = 7
	EDGE_B = 8
	NAMES = [ 'M', 'UR', 'UL', 'LL', 'LR', 'L', 'R', 'F', 'B' ]

	def __init__(self, image_set):
		self.set = image_set
		self.set_path = os.path.join(Context.terrain_dir, image_set)
		self._pil_image = None

	def get_image(self):
		"""Return a PIL image object representing this component""" 
		component_name = self._cache_path(
			self.header
			+ "_" + self.base_name()
			+ "_" + Part.NAMES[self.part]
			)
		# Do we have this cached on disk? 
		if not os.path.isfile(component_name):
			self._pil_image = self._make_part(component_name)
		# Do we have this cached in this object?
		if self._pil_image == None:
			self._pil_image = Image.open(component_name)
		return self._pil_image

	def composite(self, destination, user_mask = None):
		"""Composite ourselves into the destination image, generating
		all cached components as needed"""
		Logger.log.debug("Compositing " + self.base_name())
		
		im = self.get_image()
		if destination.size != im.size:
			im.resize(destination.size, BICUBIC)

		# Find any alpha layer in the image
		transp = None
		for band in zip(im.getbands(), im.split()):
			if band[0] == "A":
				Logger.log.debug("Found transparency layer")
				transp = band[1]

		# Decide what blending we will be doing
		if user_mask == None:
			if transp == None:
				# We have no concept of transparency at all -- use a
				# flat setting
				Logger.log.debug("Using flat mask")
				mask = Image.new("1", im.size, 1)
			else:
				# We have a transparency but no user mask
				mask = transp
		else:
			if transp == None:
				# We have a mask but no transparency -- use the user's
				# mask
				mask = user_mask
			else:
				# If we have both a supplied mask and our own
				# transparency, use both -- where either is
				# transparent, set transparency (could use
				# ImageChops.multiply() instead?)
				mask = ImageChops.darker(user_mask.convert("L"),
										 transp.convert("L"))

		return Image.composite(im, destination, mask)

	def _source_path(self, name):
		"""Return the file path for the given source image name"""
		return os.path.join(self.set_path, self.source, name + ".png")

	def _cache_path(self, name):
		"""Return the file path for the given cached partial image component"""
		return os.path.join(self.set_path, self.cache, name + ".png")
		
	def _make_part(self, name):
		"""Construct and return the image that we represent, saving it
		to cache with the given file name"""
		pass
