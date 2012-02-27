class ActionTarget(object):
    """Mix-in class for objects that can have actions bound to them."""
    def external_actions(self, player):
        acts = {}
        dicts = [self] + list(self.__class__.__mro__)
        for d in dicts:
            for k, v in vars(d).items():
                if isinstance(v, Action):
                    if k not in acts:
                        b = BoundAction(v, self, k)
                        if b.valid(player):
                            acts[k] = b
        return acts.values()


class ValidationError(Exception):
    """The action parameters did not validate."""


class ActionFailed(Exception):
    """The action could not be completed."""


class SayField(object):
    """An input field corresponding to a 'say' message box"""
    def __init__(self, name, default=''):
        self.name = name
        self.default = ''

    def clean(self, value):
        v = value.strip()
        if not v:
            raise ValidationError("You must enter a message.")
        return v

    def context_get(self):
        return {
            'name': self.name,
            'default': self.default,
        }

class ItemField(object):
    """Display an item name"""
    def __init__(self, item):
        self.item = item

    def context_get(self):
        return {
            'item': self.item.name_for()
        }

class IntegerField(object):
    def __init__(self, name, default=None):
        self.name = name
        self.default = default

    def clean(self, value):
        if not value.strip() and self.default:
            return self.default
        try:
            i = int(value.strip())
        except ValueError:
            raise ValidationError("You must enter an integer.")
        return i

    def context_get(self):
        return {
            'name': self.name,
            'default': self.default,
        }


class Action(object):
    """Something that the user can be invited to do.

    This class is the abstract base class of all actions.
    """

    group = u"Miscellaneous"
    cost = None
    caption = 'Unknown Action'

    def __init__(self, **kwargs):
        """Instantiate the action.

        Any keyword arguments passed are assigned directly to the instance
        dictionary. This is as a convenience to allow properties of the
        action to be overridden at instantiation.
        """
        self.__dict__.update(kwargs)

    def get_uid(self):
        """Return a unique ID identifying this action"""
        mod = self.__class__.__module__
        name = self.__class__.__name__
        return '%s.%s' % (mod, name)

    def get_parameters(self):
        """Get a list of the input fields required
        to process this action."""
        return None

    def can_afford(self, actor):
        if self.cost is None:
            return True
        return self.cost.can_afford(actor)

    def get_caption(self, target):
        return self.caption

    def get_kwargs(self, data):
        """Extract the parameters for the action."""
        kw = {}
        params = self.get_parameters()
        if not params:
            return {}
        for p in params:
            if not hasattr(p, 'name'):
                continue
            val = p.clean(data.get(p.name, ''))
            kw[p.name] = val
        return kw    

    def perform(self, actor, target, data):
        """Have the actor attempt to perform the action.

        data are the parameters for the action.
        """
        if self.cost:
            if not self.cost.can_afford(actor):
                raise ActionFailed("You cannot afford it!")
            self.cost.charge(actor)
        kwargs = self.get_kwargs(data)
        message = self.do(actor, target, **kwargs)
        return message

    def valid(self, actor, target):
        """Determine whether the action can be performed by actor on target."""
        return True

    def do(self, actor, *args):
        """Perform the action."""
        return "Nothing happened."

    @staticmethod
    def make_id(object, act):
        if hasattr(object, 'internal_name'):
            return "%s.%s.%s" % (object.internal_name(), object.id, act)
        return "%s.%s.%s" % (object.__class__.__name__, object.id, act)

    def context_get(self, context):
        ret = {}
        if self.cost:
            ret['cost'] = str(self.cost)
        ret['uid'] = self.get_uid()
        ret['caption'] = self.caption
        ret['group'] = self.group

        params = self.get_parameters()
        if params:
            ps = []
            for p in params:
                if hasattr(p, 'context_get'):
                    ctx = p.context_get()
                    ctx['type'] = p.__class__.__name__
                    ps.append(ctx)
                else:
                    ps.append(p)
            ret['parameters'] = ps

        return ret


class PersonalAction(Action):
    """An action that can only be performed by the actor itself."""
    def valid(self, actor, target):
        return actor is target


class LocalAction(Action):
    """An action that can only be performed if actor is in the same place as target."""
    def valid(self, actor, target):
        return actor.pos == target.pos


class BoundAction(object):
    """Bind an action to the object on which it operates."""
    def __init__(self, action, target, name):
        self.action = action
        self.target = target
        self.name = name

    def __repr__(self):
        return '<BoundAction %s on %s>' % (self.name, self.target)

    def get_uid(self):
        try:
            id = str(''.join('%02x' % ord(c) for c in self.target._p_oid))
        except AttributeError:
            id = str(self.target.id)
        return '%s/%s' % (id, self.name)

    def context_get(self, context):
        ret = self.action.context_get(context)
        ret['uid'] = self.get_uid()
        ret['caption'] = self.action.get_caption(self.target)
        ret['can_afford'] = self.action.can_afford(context.player)
        return ret

    def valid(self, actor):
        """Determine whether the action can be performed by actor."""
        return self.action.valid(actor, self.target)

    def perform(self, actor, data):
        """Perform the action on the bound target."""
        return self.action.perform(actor, self.target, data)
