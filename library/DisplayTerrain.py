import Image, ImageDraw
import os
import Location

#Used for drawing terrains.  The general idea is that if you have tavern-on-path-on-jungle, we should make three separate images, and combine them as necessary.
#All images are saved as .png files, but the original file for each terrain may be any format.  Just know that only .PNG and .GIF files really support transparency, so any JPEGs are guaranteed to not be transparent below them, at least.
#The "final" version of any image is a .png file, on the off chance we have leftover transparency.  (...but maybe we should assume opacity and do JPEG?)

#file-naming scheme:
#border_<border type>_<direction>.png is the complete image for a border type.  The directions are F (forward slash), B (back slash), L (left), and R (right).  Never displayed, but frequently used for compositing.
#terrain_<filename minus extension>_<direction>.png is the complete image for exactly one terrain type, split into five parts (UL, UR, M, LL, LR).  It may be transparent, either partially or completely.  Never displayed, but used for compositing.
#location_<terrain1>_<terrain2>_<terrainN>_<direction>.png is the complete (composited) image for that location.  It should be opaque, but there's no technical problem if it's partially transparent.  Never displayed, but used for compositing.
#render_T1_<terrain1>_<terrainN>_T2_<terrain1>_<terrainN>_B_<border>_<F or B>.png is the final, rendered corner image.  T1 is the top terrain stack, T2 is the bottom stack, B is the border type, and F or B stands for Forward Slash or Back Slash, depending on the angle of the diagonal line.
#render_T_<terrain1>_<terrainN>_B1_<left border>_B2_<right border>.png is the final, rendered body image. T is the terrain stack, B1 is the left border, B2 is the right border.

#Pulled out of my ass.  Consider it pseudocode.
def get_location_piece(stack,part):
	#file format: location_t1.t2.tN_part.png
	file_name="location_"
	is_first=True
	for loc in stack:
		if loc.terrain != None:
			if not is_first:
				is_first=false
			else:
				file_name+='.'
			file_name+=loc.terrain.split('.')[0]
	file_name+='_'+part+'.png'
	if not os.path.isfile(file_name):
		terrain=Image.new((1,1),"RGBA")
		for loc in stack:
			terr=Image.open(get_terrain_piece(loc.terrain,part))
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
	return file_name

#more ass-pulling.  Does not actually render the neighborhood, but rather ensures that all of the filenames that we send down to the browser have actual images to back them up.
#graph of locations, by index in the neighbor-list:
# 3 2
#4 0 1
# 5 6
def pre_render_neighborhood(neigh):
	return None

def get_terrain_piece(terrain_file,part):
	terrain_code=terrain_file.split('.')[0]
	file_name="terrain_"+terrain_code+"_"+part+".png"
	if (not os.path.isfile(file_name)):
		split_terrain(terrain_file)

	return file_name
	
def split_terrain(terrain_file):
	if (name!='' && name!=None):
		im=Image.open(terrain_file)
		terrain_code=terrain_file.split('.')[0]
		center_x=int(im.size[0]/2)
		top_fold=int(im.size[1]/4)
		bottom_fold=int(im.size[1]*.75)
		
		UL=im.crop((0,0,center_x,top_fold))
		UL.save("terrain_"+terrain_code+"_UL.png")
		UR=im.crop((center_x,0,im.size[0],top_fold))
		UR.save("terrain_"+terrain_code+"_UR.png")
		middle=im.crop((0,top_fold,im.size[0],bottom_fold))
		middle.save("terrain_"+terrain_code+"_M.png")
		LL=im.crop((0,bottom_fold,center_x,im.size[1]))
		LL.save("terrain_"+terrain_code+"_LL.png")
		LR=im.crop((center_x,bottom_fold,im.size[0],im.size[1]))
		LR.save("terrain_"+terrain_code+"_LR.png")
	# Blank string==boring, transparent image, suitable for edge hexes that have nothing beyond them.  Generate it if it doesn't exist yet.
	else:
		im=Image.new("LA",(1,1))
		draw=ImageDraw.Draw(im)
		draw.point((0,0),fill=(0,0))
		im.save("terrain__UL.png")
		im.save("terrain__UR.png")
		im.save("terrain__M.png")
		im.save("terrain__LL.png")
		im.save("terrain__LR.png")

def render_hex_corner(top_terr_file, bottom_terr_file, is_forward_slash, border_file):
	top_code=top_terr_file.split('.')[0]
	bottom_code=bottom_terr_file.split('.')[0]
	border_code=border_file.split('.')[0]
	
	if is_forward_slash:
		corner_type = "F"
		upper_type = "UL"
		lower_type = "LR"
	else:
		corner_type = "B"
		upper_type = "UR"
		lower_type = "LL"

	file_name="corner_T1."+top_code+'.T2.'+bottom_code+'.B.'+border_code+'_'+corner_type+'.png'
	if (not os.path.isfile(file_name)):
		top_terr=Image.open(get_terrain_piece(top_code,upper_type))
		if top_terr.mode!='RGBA':
			top_terr=top_terr.convert('RGBA')
		bottom_terr=Image.open(get_terrain_piece(bottom_code,lower_type))
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
		border=Image.open(get_border(border_code,corner_type))
		if border.mode!='RGBA':
			border=border.convert('RGBA')
		if (corner.size!=border.size):
			if (corner.size[0]*corner.size[1] > border.size[0]*border.size[1]):
				border=border.resize(corner.size,Image.BICUBIC)
			else:
				corner=corner.resize(border.size,Image.BICUBIC)
		print "First composite done.  top_terr size:"+str(top_terr.size)+"  bottom_terr size:"+str(bottom_terr.size)+"   mask size:"+str(mask.size)+"   corner size:"+str(corner.size)+"  border size:"+str(border.size)
		corner=Image.composite(border,corner,border)
		corner.save(file_name, palette=Image.ADAPTIVE)
		print "Palettes.  top:"+top_terr.mode+"  bottom:"+bottom_terr.mode+"  mask:"+mask.mode+"  border:"+border.mode+"  corner:"+corner.mode

	return file_name

def get_border(border_file, part):
	border_code=border_file.split('.')[0]
	file_name="border_"+border_code+"_"+part+".png"
	if (not os.path.isfile(file_name)):
		#if you create one angle-thing, we can make the other by flipping it.  I don't like rotation in images.
		if (part=="F" and os.path.isfile("border_"+border_code+"_B.png") or part=="B" and os.path.isfile("border_"+border_code+"_F.png")):
			other_part = part=="F" and "B" or "F"
			im=Image.open("border_"+border_code+"_"+other_part+".png")
			im=im.transpose(Image.FLIP_LEFT_RIGHT)
			im.save(file_name)
		#But if you really, really want it.... yes, we can do horrible, horrible things to your image.
		else:
			split_border(border_file)
	return file_name
			
#assumption: your border image runs vertically, smack dab in the middle of the image.		
def split_border(border_file):
	border_code=border_file.split('.')[0]
	im=Image.open(border_file)
	#yes, it's more effort to maintain left & right separately.  But maybe you have a really fancy border that you don't want to be perfectly symmetrical?
	left=im.copy();
	right=left.copy()
	left=im.transform(im.size,Image.AFFINE,(1,0,im.size[0]/2,0,1,0),Image.NEAREST)  #Don't need bicubic, we want to shift by an integer number of pixels.  Whether it's an integer or not.
	right=im.transform(im.size,Image.AFFINE,(1,0,-im.size[0]/2,0,1,0),Image.NEAREST)  
	lDraw=ImageDraw.Draw(left)
	lDraw.rectangle((int(left.size[0]/2),0,left.size[0],left.size[1]),fill=(0,0,0,0))
	rDraw=ImageDraw.Draw(right)
	rDraw.rectangle((0,0,int(left.size[0]/2),left.size[1]),fill=(0,0,0,0))
	left.save('border_'+border_code+'_L.png')
	right.save('border_'+border_code+'_R.png')
	
	#Only create the slashes if they don't already exist, because I don't like rotations if they can be avoided.
	if (not os.path.isfile('border_'+border_code+'_F.png') and not os.path.isfile('border_'+border_code+'_B.png')):
		slash=im.rotate(-60,Image.BILINEAR)
		slash=slash.crop((int(slash.size[0]/2 - slash.size[1]*(3**.5)/4),int(slash.size[1]*.25),int(slash.size[0]/2 + slash.size[1]*(3**.5)/4),int(slash.size[1]*.75)))
		slash.save('border_'+border_code+'_F.png')
		slash=slash.transpose(Image.FLIP_LEFT_RIGHT)
		slash.save('border_'+border_code+'_B.png')

def render_hex_body(terr_file, border_left_file, border_right_file):
	terr_code=terr_file.split('.')[0]
	left_code=border_left_file.split('.')[0]
	right_code=border_right_file.split('.')[0]
	file_name="middle_T."+terr_name+".B1."+left_code+".B2."+right_code+".png"
	if (not os.path.isfile(file_name)):
		terr=Image.open(get_terrain_piece(terr_file,"M"))
		left=Image.open(get_border(border_left_file,'L'))
		right=Image.open(get_border(border_right_file,'R'))
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
		
		terr=Image.composite(left,terr,left)
		terr=Image.composite(right,terr,right)
		terr.save(file_name)
	return file_name
		