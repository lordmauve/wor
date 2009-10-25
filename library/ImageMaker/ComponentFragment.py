"""An image component: A stack of images, composited together"""

import Image

import Context

class Component(object):
	def __init__(self, image_set, stack):
		self.set = image_set
		self.set_path = os.path.join(Context.terrain_dir, image_set)
		self.stack = stack

	def _cache_path(self, name):
		"""Return the file path for the given cached partial image component"""
		return os.path.join(self.set_path, "cache", name + ".png")

	def base_name(self):
		return self.stack.join(".")

	def composite(self, destination):
		"""Composite ourselves into the destination image, generating
		all cached components as needed"""
		

	def get_location_piece(img_set, stack,part):
		

		
	#file format: location_t1.t2.tN_part.png
	file_name = "location_"
	is_first=True
	for loc in stack:
		if is_first:
			is_first=False
		else:
			file_name+='.'
		file_name+=loc
	file_name+='_'+part+'.png'
	Logger.log.debug('get_location_piece filename: '+file_name)
	if not os.path.isfile(os.path.join(Context.terrain_dir, img_set, "split", file_name)):
		terrain=Image.new("RGBA",(1,1))
		for loc in stack:
			terr = Image.open(os.path.join(Context.terrain_dir, get_terrain_piece(img_set, loc, part)))
			if terr.mode!="RGBA":
				terr=terr.convert("RGBA")
			if terrain.size==(1,1):
				terrain=terr
			else:
				if terr.size > terrain.size:
					terrain.resize(terr.size,Image.BICUBIC)
				elif terr.size < terrain.size:
					terr.resize(terrain.size,Image.BICUBIC)
				terrain=Image.composite(terr,terrain,terr)
		terrain.save(os.path.join(Context.terrain_dir, img_set, "cache", file_name))
	return file_name
