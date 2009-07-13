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
	
	if array == None:
		array = [ [ None for y in range(0, size-x) ] for x in range(0, size) ]

	# Loop through the file and read its parameters
	x = 0
	for line in ifile:
		elts = line.split()
		y = 0
		for e in elts:
			tx, ty = xfm(x, y, f)
			if 0 <= tx < size and 0 <= ty < size-x:
				array[tx][ty] = e
			y += stride
		x += stride
	ifile.close()

	return (size, stride, array)
