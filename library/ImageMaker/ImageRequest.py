"""Object representing an image request through the image
requester/maker interface"""

import os.path
import Image
import ImageDraw
import ImageChops
from mod_python import apache

import Logger
import Context
import Util
from HexFragment import HexFragment
from EdgeFragment import EdgeFragment
from HexComponent import HexComponent
from EdgeComponent import EdgeComponent
from Part import Part

class ImageRequest:
	def __init__(self, image_meta, image):
		self.meta = image_meta
		self.set = image_meta["image-set"]
		self.requested_file_name = image

		# Set the base path for the terrain set
		self.set_path = \
			os.path.normpath(
				os.path.join(Context.terrain_dir, self.set))
			
	def get_image(self):
		"""Return the full path name of the requested file for this
		object, constructing it if necessary."""

		Logger.log.debug("File requested: " + self.requested_file_name)

		# Generate the file.  For now, we'll only hand out
		# completely-rendered files (plus any already-existing file).
		# Only open up the lower functions if there turns out to be
		# some good reason for it.

		# Break down the request into components
		self._get_request_components()

		if self.is_body:
			# It's a hex body
			return self._process_body()
		else:
			# It's an edge piece
			return self._process_edge()

	def _get_request_components(self):
		"""Break down the requested file name into components."""
		#format: render-T1-terrain1.terrain2.terrain3-T2-terrain4.terrain5.terrain6-B-border-<F or B>.png for corners
		#format: render-T-terrain1.terrain2.terrainN-B1-border1-B2-border2.png for hex body

		image_parts = self.requested_file_name.split('-')
		good_format = True

		# Remove the image type from the end of the request and keep
		# it for later
		last_part = image_parts[-1].split('.')
		image_parts[-1] = '.'.join(last_part[:-1])
		self.image_format = last_part[-1]

		# Do a check for correct format
		if image_parts[0] not in ("body", "edge"):
			Logger.log.info("Unknown leading name part: " + image_parts[0])
			raise apache.SERVER_RETURN, apache.HTTP_NOT_FOUND

		if len(image_parts) % 2 != 1:
			Logger.log.info("Unexpected number of name parts")
			raise apache.SERVER_RETURN, apache.HTTP_NOT_FOUND

		self.is_body = (image_parts[0] == "body")
		if self.is_body:
			allowed_list = ("T", "B0", "B3")
		else:
			allowed_list = ("T1", "T2", "B", "B1", "B2", "D")

		# Read the request details into a hash for easy retrieval,
		# constructing the image components we need
		self.request_parts = {}
		i = 1
		while(i < len(image_parts)-1):
			# More sanity-checking
			if image_parts[i] not in allowed_list:
				Logger.log.info("Image part not allowed here: " + image_parts[i])
				raise apache.SERVER_RETURN, apache.HTTP_NOT_FOUND
			# Store the components
			self.request_parts[image_parts[i]] = image_parts[i+1].split('.')
			i += 2

	def _check_cache(self, file_name):
		"""Check whether the item is in the local cache"""
		# FIXME: Handle web caching control headers here, too
		Logger.log.debug("Looking for canonical file: " + file_name)
		if os.path.isfile(file_name):
			Logger.log.debug("Sending cached file: " + file_name)
			return True
		Logger.log.debug("Didn't find file: " + self.requested_file_name + " canonicalised at " + file_name)
		return False

	def _process_body(self):
		"""Process the request as a hex body"""
		# Do some sanity checks: T must exist -- if not, create it
		if "T" not in self.request_parts:
			self.request_parts["T"] = []
		# Borders must exist
		# FIXME

		# Get the components we need
		body = HexComponent(
			self.meta,
			self.request_parts["T"],
			Part.CENTRE)
		#left = EdgeComponent(
		#	self.set,
		#	self.request_parts["B3"],
		#	Part.EDGE_L)
		#right = EdgeComponent(
		#	self.set,
		#	self.request_parts["B0"],
		#	Part.EDGE_R)

		# Canonicalise the file name
		file_name = "body-T-" + body.base_name() \
					+ "-B0-" \
					+ "-B3-" \
					+ ".png"
		file_name = os.path.join(self.set_path, "cache", file_name)
		if self._check_cache(file_name):
			return file_name

		# Paste it all together
		hgt = self.meta["image-height"]
		hstr = self.meta["stride-height"]
		
		image_size = ( self.meta["image-width"], 2*hstr - hgt )
		image = Image.new("RGBA", image_size)
		image = body.composite(image)
		#image = left.composite(image)
		#image = right.composite(image)

		# The cache name is in canonical order
		image.save(file_name)
		return file_name

	def _process_edge(self):
		"""Process the request as an edge piece"""
		# More sanity-checks:
		# B1, B2 are incompatible with B
		if ("B" in self.request_parts
			and ("B1" in self.request_parts
				 or "B2" in self.request_parts)):
			Logger.log.info("B used with one of B1 and B2")
			raise apache.SERVER_RETURN, apache.HTTP_NOT_FOUND
		# D must be present and have a single F or R following
		if "D" not in self.request_parts:
			Logger.log.info("D parameter not present")
			raise apache.SERVER_RETURN, apache.HTTP_NOT_FOUND			
		if len(self.request_parts["D"]) != 1:
			Logger.log.info("D parameter does not have exactly one dotted part")
			raise apache.SERVER_RETURN, apache.HTTP_NOT_FOUND
		if self.request_parts["D"][0] not in ("F", "R"):
			Logger.log.info("D parameter is neither F nor R")
			raise apache.SERVER_RETURN, apache.HTTP_NOT_FOUND				

		# Hang on to direction
		self.edge_forward = (self.request_parts["D"][0] == "F")

		# We must have T1 and T2 defined -- if not, create some empties
		if "T1" not in self.request_parts:
			self.request_parts["T1"] = []
		if "T2" not in self.request_parts:
			self.request_parts["T2"] = []

		upper_side = Part.HEX_LL
		lower_side = Part.HEX_UR
		direction = "B"
		if self.edge_forward:
			upper_side = Part.HEX_LR
			lower_side = Part.HEX_UL
			direction = "F"

		upper_body = HexComponent(
			self.meta,
			self.request_parts["T1"],
			upper_side)
		lower_body = HexComponent(
			self.meta,
			self.request_parts["T2"],
			lower_side)

		# Canonicalise the filename and check the cache
		file_name = "edge-T1-" + upper_body.base_name() \
					+ "-T2-" + lower_body.base_name() \
					+ "-B1-" \
					+ "-B2-" \
					+ "-D-" + direction \
					+ ".png"
		file_name = os.path.join(self.set_path, "cache", file_name)
		if self._check_cache(file_name):
			return file_name

		# This mask is full transparency at the top, so we use it for
		# drawing the bottom half of the image
		hgt = self.meta["image-height"]
		hstr = self.meta["stride-height"]
		image_size = ( self.meta["image-width"]/2, hgt - hstr )
		bottom_mask = Image.new("1", image_size, 1)
		md = ImageDraw.Draw(bottom_mask)
		if self.edge_forward:
			md.polygon( ((0, 0),
						 (image_size[0], 0),
						 (0, image_size[1])),
						fill=0)
		else:
			md.polygon( ((0, 0),
						 (image_size[0], 0),
						 (image_size[0], image_size[1])),
						fill=0)
		# FIXME: Why does this next line not invert the mask properly?
		top_mask = ImageChops.invert(bottom_mask)

		name = os.tmpnam() + ".png"
		Logger.log.debug("Saving top mask as: " + name)
		top_mask.save(name)
		name = os.tmpnam() + ".png"
		Logger.log.debug("Saving bottom mask as: " + name)
		bottom_mask.save(name)

		# Construct our image and composite it together
		image = Image.new("RGBA", image_size, (255, 255, 255, 255))
		Logger.log.debug("Request: starting compositing")
		image = upper_body.composite(image, top_mask)
		image = lower_body.composite(image, bottom_mask)
		Logger.log.debug("Request: finished compositing")

		# Save the image and return it
		image.save(file_name)
		return file_name

# def create_final_corner(top_code, bottom_code, is_forward_slash, border_code):

# 	if (not os.path.isfile(os.path.join(Context.terrain_dir,file_name))):
# 		top_terr=Image.open(os.path.join(Context.terrain_dir,get_location_piece(top_code.split('.'),upper_type)))
# 		if top_terr.mode!='RGBA':
# 			top_terr=top_terr.convert('RGBA')
# 		bottom_terr=Image.open(os.path.join(Context.terrain_dir,get_location_piece(bottom_code.split('.'),lower_type)))
# 		if bottom_terr.mode!='RGBA':
# 			bottom_terr=bottom_terr.convert('RGBA')
# 		if (top_terr.size!=bottom_terr.size):
# 			if (top_terr.size[0]*top_terr.size[1] > bottom_terr.size[0]*bottom_terr.size[1]):
# 				bottom_terr=bottom_terr.resize(top_terr.size,Image.BICUBIC)
# 			else:
# 				top_terr=top_terr.resize(bottom_terr.size,Image.BICUBIC)

# 		corner=Image.composite(top_terr,bottom_terr,mask)
		
# 		#border image must have transparency, 'cause I'm lazy.
# 		border=Image.open(os.path.join(Context.terrain_dir,get_border(border_code,corner_type)))
# 		if border.mode!='RGBA':
# 			border=border.convert('RGBA')
# 		if (corner.size!=border.size):
# 			if (corner.size[0]*corner.size[1] > border.size[0]*border.size[1]):
# 				border=border.resize(corner.size,Image.BICUBIC)
# 			else:
# 				corner=corner.resize(border.size,Image.BICUBIC)
# 		print "First composite done.  top_terr size:"+str(top_terr.size)+"  bottom_terr size:"+str(bottom_terr.size)+"   mask size:"+str(mask.size)+"   corner size:"+str(corner.size)+"  border size:"+str(border.size)
# 		corner=Image.composite(border,corner,border)
# 		corner.save(os.path.join(Context.terrain_dir,file_name), palette=Image.ADAPTIVE)
# 		print "Palettes.  top:"+top_terr.mode+"  bottom:"+bottom_terr.mode+"  mask:"+mask.mode+"  border:"+border.mode+"  corner:"+corner.mode

# 	return file_name
