"""Object representing an image request through the image
requester/maker interface"""

import os.path
import Image
import ImageDraw
from mod_python import apache

import Logger
import Context
from HexFragment import HexFragment
from EdgeFragment import EdgeFragment
from HexComponent import HexComponent
from EdgeComponent import EdgeComponent
from Part import Part

class ImageRequest:
	def __init__(self, image_set, image):
		self.set = image_set
		self.requested_file_name = image

		# Set the base path for the terrain set
		self.set_path = \
			os.path.normpath(
				os.path.join(Context.terrain_dir, self.set))
		# Check that we haven't gone outside the main terrain directory
		if not ( os.path.isdir(self.set_path)
				 and os.path.commonprefix(
					 [ Context.terrain_dir, self.set_path ]) == Context.terrain_dir ):
			req.status = apache.HTTP_NOT_FOUND
			req.write('Image set not found')
			raise apache.SERVER_RETURN			

	def get_image(self):
		"""Return the full path name of the requested file for this
		object, constructing it if necessary."""

		Logger.log.debug("File requested: " + self.requested_file_name)

		# If it's already there (and/or somebody's just asking for a
		# base file), give it to 'em.
		# FIXME: Also check cache control headers here
		expected_path = os.path.join(self.set_path, "cache", self.requested_file_name)
		if os.path.isfile(expected_path):
			Logger.log.debug("Sending cached file: " + self.requested_file_name)
			return expected_path
		
		Logger.log.debug("Didn't find file: " + self.requested_file_name)
	
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

		#if image_parts[1] == "T1":
		#	file=os.path.join(Context.terrain_dir, render_corner(terrain_set, terrain_file))
		#	Logger.log.info('full OS path to rendered file:'+file)
		#	req.sendfile(file)
		#elif image_parts[1] == "T":
		#	req.sendfile(os.path.join(Context.terrain_dir, render_body(terrain_set, terrain_file)))
		#else:
		#	req.status=apache.HTTP_NOT_FOUND
		#	req.write('Image: unsupported image type.')
		#return apache.OK


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
		if image_parts[0] != "render":
			good_format = False

		if len(image_parts) == 7:
			if image_parts[1] != "T":
				good_format = False
			if image_parts[3] != "B1":
				good_format = False
			if image_parts[5] != "B2":
				good_format = False
		elif len(image_parts) == 8:
			if image_parts[1] != "T1":
				good_format = False
			if image_parts[3] != "T2":
				good_format = False
			if image_parts[5] != "B":
				good_format = False
			if image_parts[7][0] not in ("B", "F"):
				good_format = False
		else:
			good_format = False

		if not good_format:
			req.status = apache.HTTP_NOT_FOUND
			req.write('Image: image likely not found')
			raise apache.SERVER_RETURN

		self.is_body = (len(image_parts) == 7)

		# Read the request details into a hash for easy retrieval,
		# constructing the image components we need
		self.request_parts = {}
		i = 1
		while(i < len(image_parts)-1):
			self.request_parts[image_parts[i]] = image_parts[i+1].split('.')
			i += 2
		# Direction, for edge pieces
		if not self.is_body:
			self.edge_forward = (image_parts[7][0] == "F")

	def _process_body(self):
		"""Process the request as a hex body"""
		# Do some sanity checks
		if "T" not in self.request_parts:
			self.request_parts["T"] = []

		# Get the components we need
		body = HexComponent(
			self.set,
			self.request_parts["T"],
			Part.CENTRE)
		#left = EdgeComponent(
		#	self.set,
		#	self.request_parts["B1"],
		#	Part.EDGE_L)
		#right = EdgeComponent(
		#	self.set,
		#	self.request_parts["B2"],
		#	Part.EDGE_R)

		# Paste it all together
		image = Image.new("RGBA", body.get_image().size)
		image = body.composite(image)
		#image = left.composite(image)
		#image = right.composite(image)
		
		file_name = "render-T-" + body.base_name() \
					+ "-B1-" \
					+ "-B2-" \
					+ ".png"
		file_name = os.path.join(Context.terrain_dir, self.set, "cache", file_name)
		image.save(file_name)
		return file_name

	def _process_edge(self):
		"""Process the request as an edge piece"""
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
			self.set,
			self.request_parts["T1"],
			upper_side)
		lower_body = HexComponent(
			self.set,
			self.request_parts["T2"],
			lower_side)

		# This mask is full transparency at the top, so we use it for
		# drawing the bottom half of the image
		bottom_mask = Image.new("1", upper_body.get_image().size, 1)
		md = ImageDraw.Draw(bottom_mask)
		if self.edge_forward:
			md.polygon( ((0, 0),
						 (bottom_mask.size[0], 0),
						 (0, bottom_mask.size[1])),
						fill=0)
		else:
			md.polygon( ((0, 0),
						 (bottom_mask.size[0], 0),
						 (bottom_mask.size[0], bottom_mask.size[1])),
						fill=0)

		# Construct our image and composite it together
		image = Image.new("RGBA", upper_body.get_image().size)
		image = upper_body.composite(image)
		image = lower_body.composite(image, bottom_mask)

		# Save the image and return it
		file_name = "render-T1-" + upper_body.base_name() \
					+ "-T2-" + lower_body.base_name() \
					+ "-B-" \
					+ "-" + direction \
					+ ".png"
		file_name = os.path.join(Context.terrain_dir, self.set, "cache", file_name)
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
