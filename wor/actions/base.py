from wor.cost import Cost


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

    def __init__(self, actor):
        self.actor = actor

    def get_caption(self):
        return self.caption

    def get_uid(self):
        """Return a unique ID identifying this action"""
        raise NotImplementedError("Subclasses must implement Action.get_uid")

    def get_parameters(self):
        """Get a list of the input fields required
        to process this action."""
        return None
        
    def context_get(self, context):
        ret = {}
        if self.cost:
            ret['cost'] = str(self.cost)
        ret['uid'] = self.get_uid()
        ret['caption'] = self.get_caption()
        ret['group'] = self.group
        ret['can_afford'] = self.can_afford()

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

    def can_afford(self):
        if self.cost is None:
            return True
        return self.cost.can_afford(self.actor)

    def get_kwargs(self, data):
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

    def perform(self, data):
        if self.cost:
            if not self.cost.can_afford(self.actor):
                raise ActionFailed("You cannot afford it!")
            self.cost.charge(self.actor)
        kwargs = self.get_kwargs(data)
        message = self.action(**kwargs)
        return message

    def action(self, data):
        pass

    @staticmethod
    def make_id(object, act):
        if hasattr(object, 'internal_name'):
            return "%s.%s.%s" % (object.internal_name(), object.id, act)
        return "%s.%s.%s" % (object.__class__.__name__, object.id, act)


class TargettedAction(Action):
    """An action which is directed at another actor specifically.

    """
    caption = u'Do something mysterious to %s'

    def __init__(self, actor, target):
        super(TargettedAction, self).__init__(actor)
        self.target = target

    def get_uid(self):
        mod = self.__class__.__module__
        name = self.__class__.__name__
        return '%s.%s(%d)' % (mod.lower(), name.lower(), self.target.id)

    def get_caption(self):
        return self.caption % self.target.get_name()
