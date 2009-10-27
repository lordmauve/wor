####
# Simple utilities

from Logger import log

def render_info(info, req, prefix='', indent=0):
	"""Recursively render the data in info into the request object"""
	for k, v in info.iteritems():
		if isinstance(v, dict):
			render_info(v, req, prefix + k + '.', indent-len(prefix))
		else:
			fmt = "%-" + str(indent+1) + "s%s\n"
			key = prefix + k + ':'
			value = str(v).replace('\n', '\n ')
			req.write(fmt % (key, value))

def render_table(info, req):
	"""Render a table of data into the request object"""
	for item in info:
		# Make the input "safe" for rendering
		data = [ str(x).replace('\n', '\n ') for x in item ]
		# Join it up into table format
		req.write(':'.join(data) + '\n')

def info_key_length(info):
	"""Get the maximum key length of the given info dictionary"""
	length = 0
	for k, v in info.iteritems():
		if isinstance(v, dict):
			length = max(length, len(k)+1+info_key_length(v))
		else:
			length =max(length, len(k))
	return length


def match_id(actid, obj, uid=None):
	"""Say whether the split-up action descriptor actid matches the
	object and action name. If actid is None, match anything."""
	if actid == None:
		return True
			
	if uid == None:
		return (actid[0] == obj.ob_type()
				and actid[1] == obj._id)
		
	return (actid[0] == obj.ob_type()
			and actid[1] == obj._id
			and actid[2] == uid)

def parse_input(req):
	"""Parse input text into a hash"""
	result = {}
	k = '.'
	while True:
		# Get the next line of input
		line = req.readline()
		if line == '': # EOF
			break
		# Remove the trailing /n and/or /r
		line = line.rstrip('\n\r')
		if line == '': # Empty line
			continue

		# Process the input
		if line[0] == '-':
			return result
		elif line[0] == ' ':
			result[k] = result.get(k, '') + line[1:]
		else:
			parts = line.split(':', 2)
			if len(parts) < 2:
				continue
			k = parts[0]
			v = parts[1]
			result[k] = v

	log.debug("Parsed input: " + repr(result))
	return result

class WorError(Exception):
	"""Base Exception for all WOR code.  Subclass if needed"""
	pass
