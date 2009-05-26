#########
# Representative of a coordinate: also includes orientation

class Position:
	def __init__(self, x, y, layer):
		self.x = x
		self.y = y
		self.layer = layer

	def context_get(self):
		return { 'x': self.x,
				 'y': self.y,
				 'layer': self.layer }

	def distance(self, them):
		"""Compute the Euclidean distance between this position and
		the position of"them"."""
		return sqrt(self.distance_squared(them))

	def distance_squared(self, them):
		"""Compute the square of the Euclidean distance between this
		position and the position of "them"."""

		# The metric we use is a dot-product on a non-orthonormal
		# basis. Our unit basis vectors are (1, 0) and (1/2,
		# sqrt(3)/2) in the cartesian system, and point East and
		# North-East respectively. Thus, North-West is (-1/2,
		# sqrt(3)/2) in the cartesian system, and (-1, 1) in our
		# internal system.

		# The conversion from internal to cartesian coordinates is
		# through the matrix:
		# S = ( 1  1/2		)
		#	 ( 0  sqrt(3)/2  )
		# The Euclidean metric is therefore expressed as:
		# |s|^2 = s . s
		#	   = s^T I s
		#	   = (St)^T I (St)
		#	   = t S^T S t
		# We can precompute S^T S:
		# S^T S = (  1  1/2 )
		#		 ( 1/2  1  )
		# And therefore the Euclidean metric within our internal basis
		# is:
		# |x|^2 = x_0^2 + x_0 x_1 + x_1^2
		x0 = self.x - them.x
		x1 = self.y - them.y

		return x0 * x0 + x0 * x1 + x1 * x1

	def hop_distance(self, them):
		"""Computes the number of hex hops between here and there."""
		dx = self.x - them.x
		dy = self.y - them.y

		return max(abs(dx), abs(dy), abs(dx+dy))
