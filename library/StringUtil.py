# coding: utf-8
########
# General String Utilities.  Independent from Util because that's turning into
# a bit of a dumping ground already

import random

def random_template(template, placeholder_lists):
    """Creates a string by filling in the given template with an element at 
       random from each of the given placeholder lists."""
    # Seed the RNG
    random.seed()
    
    # Pull a single element at random out of each placeholder list
    placeholders = []
    for plist in placeholder_lists:
        placeholder = random.choice(plist)
        placeholders.append(placeholder)
    
    # Now our list of placeholders should go together quite nicely with the 
    # template we were given.  Well, it will once it's converted to a tuple
    return template % tuple(placeholders)


