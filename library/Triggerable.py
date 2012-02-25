####
# Deal with objects that can have triggers attached to their properties

class Triggerable(object):
    """Mixin class for objects that can have triggers attached to
    their properties, or to a default value"""

    def __init__(self, default_key='value'):
        self.value_triggers = {}
        self.__default_key = default_key

    def register_trigger(self, trigger, key):
        """Called by a Trigger to register it with us as interested in
        particular value change events"""
        if key not in self.value_triggers:
            self.value_triggers[key] = []
        self.value_triggers[key].append(trigger)

    def unregister_trigger(self, trigger, key):
        """Called by a trigger to unregister itself"""
        self.value_triggers[key].remove(trigger)

    def __setattr__(self, key, value):
        """Called when setting a property on this object, e.g. setting
        a value via obj.key = value"""
        if key[0] != '_':
            # Get the original value of the attribute
            old = 0
            if key in self.__dict__:
                old = self.__dict__[key]
            # Set the new value of the attribute
            self.__dict__[key] = value
            # Call the triggers
            self.__call_triggers(key, old, value)
        else:
            # Set the new value of the attribute
            self.__dict__[key] = value

    def __call_triggers(self, key, old, new):
        """Iterate through the triggers for this key, if there are any"""
        try:
            for t in self.value_triggers.get(key, []):
                t.change(key, old, new)
        except AttributeError:
            # Deal with older code that didn't have value_triggers
            # defined
            if not hasattr(self, "value_triggers"):
                self.value_triggers = {}
