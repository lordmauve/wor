import sys

SCALE = 8

def load_to_array(array, f, xfm):
	ifile = open(f['file'], 'r')

	# Read file parameters: size
	bits = ifile.next().split(' ')
	size = int(bits[0])
	# ... and stride
	stride = 1
	if len(bits) > 1:
		stride = int(bits[1])
	sys.stderr.write(f['file'] + " stride = " + str(stride) + "\n")

	# Loop through the file and read its parameters
	x = 0
	for line in ifile:
		elts = line.split()
		y = 0
		for e in elts:
			tx, ty = xfm(x, y, f)
			if 0 <= tx <= (1<<SCALE) and 0 <= ty <= (1<<SCALE)-x:
				array[tx][ty] = e
			y += stride
		x += stride
	ifile.close()
