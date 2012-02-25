"""Strategy class: applicable to a SerObject, can replace methods."""

def override(strategy_method):
    """Decorator to indicate which methods of the strategy class are
    ones that override the subject.
    """
    # Return a wrapper that takes a list of similarly-wrapped
    # functions, and calls the strategy method.
    def wrapper(obj, fn_list, args, keys):
        # The wrapper, when called, constructs a trampoline to pass as
        # the next function to call in the list. This trampoline hides
        # the function list away from the strategy class's code.
        def next_function(*next_args, **next_keys):
            first_wrapper = fn_list.pop()
            return first_wrapper(obj, fn_list, next_args, next_keys)

        # We only pass a next_function property if the method has one:
        # the original method does not have it, but all the others do.
        if fn_list:
            keys["next_function"] = next_function
        return strategy_method(*args, **keys)

    # Set this method in the class def as an overriding method
    wrapper.is_strategy_method = True
    return wrapper


class StrategyMeta(type):
    """Metaclass that enumerates the @override methods in the class
    being constructed, and makes a list of them as a class property
    for use by Strategied classes."""
    def __new__(cls, name, bases, classdict):
        classdict["methods"] = []
        rv = type.__new__(cls, name, bases, classdict)
        for item in classdict:
            if getattr(classdict[item], "is_strategy_method", False):
                rv.methods.append(item)
        return rv


class Strategy(object):
    __metaclass__ = StrategyMeta

    @staticmethod
    def applied(me):
        """Function called when this strategy class is applied. Note
        that me is not this class, but the parent class."""
        pass

    @staticmethod
    def removed(me):
        """Function called when this strategy class is applied. Note
        that me is not this class, but the parent class."""
        pass
