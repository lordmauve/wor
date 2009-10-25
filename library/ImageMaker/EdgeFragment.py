# coding=utf-8
"""Fragment class for a component of an edge"""

from ImageFragment import ImageFragment

class EdgeFragment(ImageFragment):
	header = "edge"
	
	def __init__(self, image_set, image, part):
		super(ImageFragment, self).__init__(self, image_set, image)
		self.part = part

	def _make_part(self):
		"""Take a full border image, and generate the four pieces from
		which we can make full images"""

		# Assumption: your border image runs vertically, smack dab in
		# the middle of the image.
		if self.image != "" and self.image != None:
			im = Image.open(self._source_path(self.image))
			# Yes, it's more effort to maintain left & right separately.
			# But maybe you have a really fancy border that you don't want
			# to be perfectly symmetrical?

			# Shouild really work out the semantics of
			# asymmetric borders, the internal data model,
			# and how this is communicated in the REST API
			left = im.copy()
			right = left.copy()
			# Don't need bicubic, we want to shift by an integer number of pixels.  Whether it's an integer or not.
			left = im.transform(im.size, Image.AFFINE, (1,0,im.size[0]/2,0,1,0), Image.NEAREST)
			right = im.transform(im.size, Image.AFFINE, (1,0,-im.size[0]/2,0,1,0), Image.NEAREST)  
			lDraw = ImageDraw.Draw(left)
			lDraw.rectangle((int(left.size[0]/2), 0, left.size[0], left.size[1]), fill = (0,0,0,0))
			rDraw = ImageDraw.Draw(right)
			rDraw.rectangle((0, 0, int(left.size[0]/2), left.size[1]), fill = (0,0,0,0))
			left.save(self._cache_path(self.header + "_" + self.image + "_L"))
			right.save(self._cache_path(self.header + "_" + self.image + "_R"))

			# Only create the slashes if they don't already exist,
			# because I don't like rotations if they can be avoided.
			if (not os.path.isfile(self._cache_path(self.header + "_" + self.image + "_F"))
				and not os.path.isfile(self._cache_path(self.header + "_" + self.image + "_B"))):
				slash = im.rotate(-60,Image.BILINEAR)
				slash = slash.crop(
					(int(slash.size[0]/2 - slash.size[1]*math.sqrt(3)/4),
					 int(slash.size[1]*.25),
					 int(slash.size[0]/2 + slash.size[1]*math.sqrt(3)/4),
					 int(slash.size[1]*.75)
					 )
					)
				slash.save(self._cache_path(self.header + "_" + self.image + "_F"))
				slash = slash.transpose(Image.FLIP_LEFT_RIGHT)
				# FIXME: Do a second rotation of 60° for this border
				slash.save(self._cache_path(self.header + "_" + self.image + "_B"))
				# FIXME: Two more rotations (or flips) to get the other two edge parts
		else:
			# Blank name: empty image -- generate them if they don't exist
			im = Image.new("LA", (1, 1))
			draw = ImageDraw.Draw(im)
			draw.point((0, 0), fill = (0, 0))
			im.save(self._cache_path(self.header + "__L"))
			im.save(self._cache_path(self.header + "__R"))
			im.save(self._cache_path(self.header + "__F"))
			im.save(self._cache_path(self.header + "__B"))

		return Image.open(
			self._cache_path(
				self.header
				+ "_" + self.image
				+ "_" + Part.NAMES[self.part]
				)
			)
