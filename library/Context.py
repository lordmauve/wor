"""Context for requests."""

context = None

# Administrator access
ADMIN = 0
# Owner access
OWNER = 1
# Access given to friends: entity visible
FRIEND_VISIBLE = 2
# Access given to friends: entity invisible
FRIEND_INVISIBLE = 3
# Default access, given to everyone else: entity visible
STRANGER_VISIBLE = 4
# Default access, given to everyone else: entity invisible
STRANGER_INVISIBLE = 5

def authz_actor(actor):
	"""Return the degree of data that can be returned w.r.t. the
	current context."""
	# Administrators
	if context['admin']:
		return ADMIN

	if context == actor:
		return OWNER

	if context.loc()._id == actor.loc()._id:
		return STRANGER_VISIBLE

	return STRANGER_INVISIBLE

def authz_location(loc):
	"""Return the degree of data that can be returned w.r.t. the
	current context."""
	if context['admin']:
		return ADMIN

	if context._id == loc.owner()._id:
		return OWNER

	if context.loc().pos.hop_distance(loc.pos) <= context.power('sight'):
		return STRANGER_VISIBLE

	return STRANGER_INVISIBLE

def authz_item(item):
	if context['admin']:
		return ADMIN

	return STRANGER_INVISIBLE