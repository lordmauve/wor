"""A stack of hex body bits composited together"""

import os.path
import Image

import Logger
from Component import Component
from HexFragment import HexFragment

class HexComponent(Component):
    header = "hex"
    
    def __init__(self, meta, stack, part):
        super(HexComponent, self).__init__(meta, stack)
        self.part = part

    def _make_part(self, component_name):
        Logger.log.debug("Building hex component for " + self.base_name())
        # Get the fragments we need to put ourself together
        fragments = [ HexFragment(self.meta, name, self.part)
                      for name in self.stack ]

        # Get the base image size we should be using from the first
        # image fragment
        if len(fragments) == 0:
            size = (1,1)
        else:
            size = fragments[0].get_image().size
        Logger.log.debug("Image size is " + str(size))
        
        # Create a base image
        base = Image.new("RGBA", size)

        # Composite each image into it
        for frag in fragments:
            base = frag.composite(base)

        # Save the image to the cache
        base.save(component_name)
        
        return base
