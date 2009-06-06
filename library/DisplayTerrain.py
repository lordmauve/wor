import Image, ImageDraw
import os
import Location

#Pulled out of my ass.  Consider it pseudocode.
def get_location_piece(stack,part):
	file_name="location"
	for loc in stack:
		file_name+='_'+loc.terrain
	file_name+='.png'
	if not os.path.isfile(file_name):
		terrain=Image.new((1,1),"RGBA")
		for loc in stack:
			terr=Image.open(get_terrain_piece(loc.terrain))
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

#more ass-pulling.
def render_neighborhood(neigh):
	return None

def get_terrain_piece(type,part):
	file_name="terrain_"+type+"_"+part+".png"
	if (not os.path.isfile(file_name)):
		split_terrain(type)

	return file_name
	
def split_terrain(name):
	if (name!=''):
		im=Image.open(name+'.png')
		center_x=int(im.size[0]/2)
		top_fold=int(im.size[1]/4)
		bottom_fold=int(im.size[1]*.75)
		
		UL=im.crop((0,0,center_x,top_fold))
		UL.save("terrain_"+name+"_UL.png")
		UR=im.crop((center_x,0,im.size[0],top_fold))
		UR.save("terrain_"+name+"_UR.png")
		middle=im.crop((0,top_fold,im.size[0],bottom_fold))
		middle.save("terrain_"+name+"_M.png")
		LL=im.crop((0,bottom_fold,center_x,im.size[1]))
		LL.save("terrain_"+name+"_LL.png")
		LR=im.crop((center_x,bottom_fold,im.size[0],im.size[1]))
		LR.save("terrain_"+name+"_LR.png")
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

def render_hex_corner(top_terr_name, bottom_terr_name, is_forward_slash, border_type):
	file_name="corner_"+top_terr_name+'_'+bottom_terr_name+'_'+(is_forward_slash and "F" or "B")+'_'+border_type+'.png'
	if (not os.path.isfile(file_name)):
		top_terr=Image.open(get_terrain_piece(top_terr_name,is_forward_slash and "UL" or "UR"))
		if top_terr.mode!='RGBA':
			top_terr=top_terr.convert('RGBA')
		bottom_terr=Image.open(get_terrain_piece(bottom_terr_name,is_forward_slash and "LR" or "LL"))
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
		border=Image.open(get_border(border_type,(is_forward_slash and "F" or "B")))
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

def get_border(name, part):
	file_name="border_"+name+"_"+part+".png"
	if (not os.path.isfile(file_name)):
		#if you create one angle-thing, we can make the other by flipping it.  I don't like rotation in images.
		if (part=="F" and os.path.isfile("border_"+name+"_B.png") or part=="B" and os.path.isfile("border_"+name+"_F.png")):
			other_part = part=="F" and "B" or "F"
			im=Image.open("border_"+name+"_"+other_part+".png")
			im=im.transpose(Image.FLIP_LEFT_RIGHT)
			im.save(file_name)
		#But if you really, really want it.... yes, we can do horrible, horrible things to your image.
		else:
			split_border(name)
	return file_name
			
#assumption: your border image runs vertically, smack dab in the middle of the image.		
def split_border(name):
	im=Image.open(name+'.png')
	#yes, it's more effort to maintain left & right separately.  But maybe you have a really fancy border that you don't want to be perfectly symmetrical?
	#(also: I am lazy.  There's an ImageChops function that wraps on translation.)
	left=im.copy();
	right=left.copy()
	left=im.transform(im.size,Image.AFFINE,(1,0,im.size[0]/2,0,1,0),Image.NEAREST)  #Don't need bicubic, we want to shift by an integer number of pixels.  Whether it's an integer or not.
	right=im.transform(im.size,Image.AFFINE,(1,0,-im.size[0]/2,0,1,0),Image.NEAREST)  
	lDraw=ImageDraw.Draw(left)
	lDraw.rectangle((int(left.size[0]/2),0,left.size[0],left.size[1]),fill=(0,0,0,0))
	rDraw=ImageDraw.Draw(right)
	rDraw.rectangle((0,0,int(left.size[0]/2),left.size[1]),fill=(0,0,0,0))
	left.save('border_'+name+'_L.png')
	right.save('border_'+name+'_R.png')
	
	#Only create the slashes if they don't already exist, because I don't like rotations if they can be avoided.
	if (not os.path.isfile('border_'+name+'_F.png') and not os.path.isfile('border_'+name+'_B.png')):
		slash=im.rotate(-60,Image.BILINEAR)
		slash=slash.crop((int(slash.size[0]/2 - slash.size[1]*(3**.5)/4),int(slash.size[1]*.25),int(slash.size[0]/2 + slash.size[1]*(3**.5)/4),int(slash.size[1]*.75)))
		slash.save('border_'+name+'_F.png')
		slash=slash.transpose(Image.FLIP_LEFT_RIGHT)
		slash.save('border_'+name+'_B.png')

def render_hex_body(terr_name, border_left_name, border_right_name):
	file_name="middle_"+terr_name+"_"+border_left_name+"_"+border_right_name+".png"
	if (not os.path.isfile(file_name)):
		terr=Image.open(get_terrain_piece(terr_name,"M"))
		left=Image.open(get_border(border_left_name,'L'))
		right=Image.open(get_border(border_right_name,'R'))
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
		