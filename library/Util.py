####
# Simple utilities

def default(v, d=0):
    """If v is defined, return v. Otherwise, return d."""
    try:
        if v != None:
            return v
        return d
    except AttributeError:
        return d
