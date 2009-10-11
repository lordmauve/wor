#######
# Handlers for image requests

import sys
import os
import traceback
import Image
import ImageDraw
from mod_python import apache

import Context
from Database import DB
import Logger

#can't assign the full terrain directory until we have the "wor.root_path" PythonOption, accessable from the request object.
TERRAIN_DIR=''

#First shot at a handler will only take on the <server>/img/terrain/thingy.png requests
def image_handler(req):
	try:
		Context.set_request_id()
		return image_handler_core(req)
	except apache.SERVER_RETURN, ex:
		# Catch and re-raise apache/mod_python exceptions here
		raise
	except Exception, ex:
		# Catch any other exception

		# Set up a simple Infernal Server Error response 
		req.status = apache.HTTP_INTERNAL_SERVER_ERROR
		req.write("There was an infernal server error. Please report this (with reference %s) to the admins.\n" % (Context.request_id))

		# Get the details of the last exception
		exlist = sys.exc_info()
		# Get a list of text lines (possibly with embedded \n)
		# describing the full backtrace
		exdata = traceback.format_exception(exlist[0], exlist[1], exlist[2])
		# Write those lines to the exception log
		head = Logger.header % { 'stamp': Context.request_time, 'req': Context.request_id }
		Logger.exception_log.error(head + ''.join(exdata))

		# Return the Infernal Server Error
		return apache.OK

def image_handler_core(req):
	pyOpts=req.get_options()
	global TERRAIN_DIR
	TERRAIN_DIR=os.path.join(pyOpts['wor.root_path'],'server_root','img','terrain')
	components = req.uri.split('/')
	Logger.log.debug('image_handler entered: URL components:'+str(components)+'  TERRAIN_DIR:'+TERRAIN_DIR)
	if components.pop(0) != '':
		# No leading slash -- something's screwy
		req.status = apache.HTTP_INTERNAL_SERVER_ERROR
		req.write("No leading slash on request for URL '"+req.uri+"'")
		return apache.OK

	if components.pop(0) != 'img':
		req.status = apache.HTTP_INTERNAL_SERVER_ERROR
		req.write("Incorrect path prefix on request for URL '"+req.uri+"'")
		return apache.OK
		
	if components.pop(0) != 'terrain':
		req.status = apache.HTTP_NOT_FOUND
		req.write('Image: image group not handled')
		return apache.OK
	terrain_file=components.pop(0)
	
	Logger.log.debug('file requested: '+terrain_file)
	
	#if it's already there (and/or somebody's just asking for a base file), give it to 'em.
	if os.path.isfile(os.path.join(TERRAIN_DIR,terrain_file)):
		Logger.log.debug('just sending base file: '+terrain_file)
		req.sendfile(os.path.join(TERRAIN_DIR,terrain_file))
		return apache.OK
		
	Logger.log.debug('didn\'t find file: '+terrain_file)
	
	#generate the file.  For now, we'll only hand out completely-rendered files (plus any already-existing file).  Only open up the lower functions if there turns out to be some good reason for it.
	#format: render-T1-terrain1.terrain2.terrain3-T2-terrain4.terrain5.terrain6-B-border-<F or B>.png for corners
	#format: render-T-terrain1.terrain2.terrainN-B1-border1-B2-border2.png for hex body
	
	# Break down the image name into separate components and check
	# that it's sane
	image_parts = terrain_file.split('-')
	good_format = True

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
		return apache.OK
		
	if image_parts[1] == "T1":
		file=os.path.join(TERRAIN_DIR,render_corner(terrain_file))
		Logger.log.info('full OS path to rendered file:'+file)
		req.sendfile(file)
		return apache.OK
		
	elif image_parts[1] == "T":
		req.sendfile(os.path.join(TERRAIN_DIR,render_body(terrain_file)))
		return apache.OK
	
	else:
		req.status=apache.HTTP_NOT_FOUND
		req.write('Image: unsupported image type.')
		return apache.OK


def render_corner(terrain_file):
	"""Process the file name, and extract what needs to be rendered
	for a hex corner image."""
	t2_loc=terrain_file.find('-T2-')
	top_location=terrain_file[10:t2_loc]
	b_loc=terrain_file.find('-B-')
	bottom_location=terrain_file[t2_loc+4:b_loc]
	end_loc=terrain_file.find('.png')
	border=terrain_file[b_loc+3:end_loc-2]
	if (terrain_file[end_loc-1]=='B'):
		is_forward_slash=False
	elif (terrain_file[end_loc-1]=='F'):
		is_forward_slash=True
	
	return create_final_corner(top_location,bottom_location,is_forward_slash,border)

def render_body(terrain_file):
	"""Process the file name, and extract what needs to be rendered
	for a hex body image"""
	b1_loc=terrain_file.find('-B1-')
	location=terrain_file[9:b1_loc] #location of the first character after "render-T-"
	b2_loc=terrain_file.find('-B2-')
	left_border=terrain_file[b1_loc+4:b2_loc]
	end_loc=terrain_file.find('.png')
	right_border=terrain_file[b2_loc+4:end_loc]
	Logger.log.debug('render components for render_body: '+location+'  '+left_border+'   '+right_border)
	return create_final_body(location,left_border,right_border)




def get_location_piece(stack,part):
	#file format: location_t1.t2.tN_part.png
	file_name="location_"
	is_first=True
	for loc in stack:
		if is_first:
			is_first=False
		else:
			file_name+='.'
		file_name+=loc
	file_name+='_'+part+'.png'
	Logger.log.debug('get_location_piece filename: '+file_name)
	if not os.path.isfile(os.path.join(TERRAIN_DIR,file_name)):
		terrain=Image.new("RGBA",(1,1))
		for loc in stack:
			terr=Image.open(os.path.join(TERRAIN_DIR,get_terrain_piece(loc,part)))
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
		terrain.save(os.path.join(TERRAIN_DIR,file_name))
	return file_name


def get_terrain_piece(terrain,part):
	file_name="terrain_"+terrain+"_"+part+".png"
	if (not os.path.isfile(os.path.join(TERRAIN_DIR,file_name))):
		split_terrain(terrain)

	return file_name
	
def split_terrain(terrain):
	"""Take a full terrain image tile and fragment it into the five
	pieces we can construct rendered images from""" 
	if (terrain!='' and terrain!=None):
		im=Image.open(os.path.join(TERRAIN_DIR,terrain+'.png'))
		center_x=int(im.size[0]/2)
		top_fold=int(im.size[1]/4)
		bottom_fold=int(im.size[1]*.75)
		
		UL=im.crop((0,0,center_x,top_fold))
		UL.save(os.path.join(TERRAIN_DIR,"terrain_"+terrain+"_UL.png"))
		UR=im.crop((center_x,0,im.size[0],top_fold))
		UR.save(os.path.join(TERRAIN_DIR,"terrain_"+terrain+"_UR.png"))
		middle=im.crop((0,top_fold,im.size[0],bottom_fold))
		middle.save(os.path.join(TERRAIN_DIR,"terrain_"+terrain+"_M.png"))
		LL=im.crop((0,bottom_fold,center_x,im.size[1]))
		LL.save(os.path.join(TERRAIN_DIR,"terrain_"+terrain+"_LL.png"))
		LR=im.crop((center_x,bottom_fold,im.size[0],im.size[1]))
		LR.save(os.path.join(TERRAIN_DIR,"terrain_"+terrain+"_LR.png"))
	# Blank string==boring, transparent image, suitable for edge hexes that have nothing beyond them.  Generate it if it doesn't exist yet.
	else:
		im=Image.new("LA",(1,1))
		draw=ImageDraw.Draw(im)
		draw.point((0,0),fill=(0,0))
		im.save(os.path.join(TERRAIN_DIR,"terrain__UL.png"))
		im.save(os.path.join(TERRAIN_DIR,"terrain__UR.png"))
		im.save(os.path.join(TERRAIN_DIR,"terrain__M.png"))
		im.save(os.path.join(TERRAIN_DIR,"terrain__LL.png"))
		im.save(os.path.join(TERRAIN_DIR,"terrain__LR.png"))

def create_final_corner(top_code, bottom_code, is_forward_slash, border_code):
	"""Create a corner image, given the image names for the two
	halves, plus that of the border on this edge"""
	if is_forward_slash:
		corner_type="F"
		upper_type = "LR"
		lower_type = "UL"
	else:
		corner_type = "B"
		upper_type = "LL"
		lower_type = "UR"

	file_name="render-T1-"+top_code+'-T2-'+bottom_code+'-B-'+border_code+'-'+corner_type+'.png'
	if (not os.path.isfile(os.path.join(TERRAIN_DIR,file_name))):
		top_terr=Image.open(os.path.join(TERRAIN_DIR,get_location_piece(top_code.split('.'),upper_type)))
		if top_terr.mode!='RGBA':
			top_terr=top_terr.convert('RGBA')
		bottom_terr=Image.open(os.path.join(TERRAIN_DIR,get_location_piece(bottom_code.split('.'),lower_type)))
		if bottom_terr.mode!='RGBA':
			bottom_terr=bottom_terr.convert('RGBA')
		if (top_terr.size!=bottom_terr.size):
			if (top_terr.size[0]*top_terr.size[1] > bottom_terr.size[0]*bottom_terr.size[1]):
				bottom_terr=bottom_terr.resize(top_terr.size,Image.BICUBIC)
			else:
				top_terr=top_terr.resize(bottom_terr.size,Image.BICUBIC)
		mask=Image.new("1", top_terr.size)
		mask_draw=ImageDraw.Draw(mask)
		if is_forward_slash:
			mask_draw.polygon(((0,0),(0,mask.size[1]),(mask.size[0],0)), fill=1)
		else:
			mask_draw.polygon(((0,0),(mask.size[0],mask.size[1]),(mask.size[0],0)), fill=1)
		corner=Image.composite(top_terr,bottom_terr,mask)
		
		#border image must have transparency, 'cause I'm lazy.
		border=Image.open(os.path.join(TERRAIN_DIR,get_border(border_code,corner_type)))
		if border.mode!='RGBA':
			border=border.convert('RGBA')
		if (corner.size!=border.size):
			if (corner.size[0]*corner.size[1] > border.size[0]*border.size[1]):
				border=border.resize(corner.size,Image.BICUBIC)
			else:
				corner=corner.resize(border.size,Image.BICUBIC)
		print "First composite done.  top_terr size:"+str(top_terr.size)+"  bottom_terr size:"+str(bottom_terr.size)+"   mask size:"+str(mask.size)+"   corner size:"+str(corner.size)+"  border size:"+str(border.size)
		corner=Image.composite(border,corner,border)
		corner.save(os.path.join(TERRAIN_DIR,file_name), palette=Image.ADAPTIVE)
		print "Palettes.  top:"+top_terr.mode+"  bottom:"+bottom_terr.mode+"  mask:"+mask.mode+"  border:"+border.mode+"  corner:"+corner.mode

	return file_name

def get_border(border, part):
	file_name="border_"+border+"_"+part+".png"
	if (not os.path.isfile(os.path.join(TERRAIN_DIR,file_name))):
		#if you create one angle-thing, we can make the other by flipping it.  I don't like rotation in images.
		if (part=="F" and os.path.isfile(os.path.join(TERRAIN_DIR,"border_"+border+"_B.png")) or part=="B" and os.path.isfile(os.path.join(TERRAIN_DIR,"border_"+border+"_F.png"))):
			other_part = part=="F" and "B" or "F"
			im=Image.open(os.path.join(TERRAIN_DIR,"border_"+border+"_"+other_part+".png"))
			im=im.transpose(Image.FLIP_LEFT_RIGHT)
			im.save(os.path.join(TERRAIN_DIR,file_name))
		#But if you really, really want it.... yes, we can do horrible, horrible things to your image.
		else:
			split_border(border)
	return file_name
			
#assumption: your border image runs vertically, smack dab in the middle of the image.		
def split_border(border):
	if border != "" and border != None:
		im=Image.open(os.path.join(TERRAIN_DIR,border+'.png'))
		# Yes, it's more effort to maintain left & right separately.
		# But maybe you have a really fancy border that you don't want
		# to be perfectly symmetrical?
		left=im.copy();
		right=left.copy()
		left=im.transform(im.size,Image.AFFINE,(1,0,im.size[0]/2,0,1,0),Image.NEAREST)  #Don't need bicubic, we want to shift by an integer number of pixels.  Whether it's an integer or not.
		right=im.transform(im.size,Image.AFFINE,(1,0,-im.size[0]/2,0,1,0),Image.NEAREST)  
		lDraw=ImageDraw.Draw(left)
		lDraw.rectangle((int(left.size[0]/2),0,left.size[0],left.size[1]),fill=(0,0,0,0))
		rDraw=ImageDraw.Draw(right)
		rDraw.rectangle((0,0,int(left.size[0]/2),left.size[1]),fill=(0,0,0,0))
		left.save(os.path.join(TERRAIN_DIR,'border_'+border+'_L.png'))
		right.save(os.path.join(TERRAIN_DIR,'border_'+border+'_R.png'))
	
		#Only create the slashes if they don't already exist, because I don't like rotations if they can be avoided.
		if (not os.path.isfile(os.path.join(TERRAIN_DIR,'border_'+border+'_F.png')) and not os.path.isfile(os.path.join(TERRAIN_DIR,'border_'+border+'_B.png'))):
			slash=im.rotate(-60,Image.BILINEAR)
			slash=slash.crop((int(slash.size[0]/2 - slash.size[1]*(3**.5)/4),int(slash.size[1]*.25),int(slash.size[0]/2 + slash.size[1]*(3**.5)/4),int(slash.size[1]*.75)))
			slash.save(os.path.join(TERRAIN_DIR,'border_'+border+'_F.png'))
			slash=slash.transpose(Image.FLIP_LEFT_RIGHT)
			slash.save(os.path.join(TERRAIN_DIR,'border_'+border+'_B.png'))
	else:
		# Blank name: empty image -- generate them if they don't exist
		im = Image.new("LA", (1, 1))
		draw = ImageDraw.Draw(im)
		draw.point((0, 0), fill = (0, 0))
		im.save(os.path.join(TERRAIN_DIR, "border__L.png"))
		im.save(os.path.join(TERRAIN_DIR, "border__R.png"))
		im.save(os.path.join(TERRAIN_DIR, "border__F.png"))
		im.save(os.path.join(TERRAIN_DIR, "border__B.png"))

def create_final_body(terr_code, left_border, right_border):
	file_name="render-T-"+terr_code+"-B1-"+left_border+"-B2-"+right_border+".png"
	if (not os.path.isfile(os.path.join(TERRAIN_DIR,file_name))):
		terr=Image.open(os.path.join(TERRAIN_DIR,get_location_piece(terr_code.split('.'),"M")))
		left=Image.open(os.path.join(TERRAIN_DIR,get_border(left_border,'L')))
		right=Image.open(os.path.join(TERRAIN_DIR,get_border(right_border,'R')))
		largest=None
		images=[terr,left,right]
		for i in images:
			if i.size > largest:
				largest=i.size
		
		if (terr.size<largest):
			terr=terr.resize(largest,Image.BICUBIC)
		if (left.size<largest):
			left=left.resize(largest,Image.BICUBIC)
		if (right.size<largest):
			right=right.resize(largest,Image.BICUBIC)

		# FIXME: This throws a bad transparency mask
		#terr=Image.composite(left,terr,left)
		#terr=Image.composite(right,terr,right)
		terr.save(os.path.join(TERRAIN_DIR,file_name))
	return file_name
