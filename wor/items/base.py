# coding: utf-8

import random
from persistent import Persistent

import Util
import BaseConfig
from wor.plan import makeable_plans
import Context

from wor.db import db
from wor.actions.make import ActionMake
from wor.jsonutil import JSONSerialisable


class InsufficientItemsException(Exception):
    """An attempt was made to remove a number of items from a
    collection when that number was not present."""
    

class Item(JSONSerialisable, Persistent):
    """An item. By default, all items are unique. Some items are
    'aggregate' and represent a block of otherwise identical things --
    e.g. coins -- and can be combined and split (see AggregateItem).
    """
    __abstract = True    # declares the item as abstract so it won't appear in list_all_classes

    group = "General"

    # Default failure function is a mean life of 300, and equal
    # probability of failing on each use.
    break_profile = lambda life: weibull(life, 300.0, 1.0)

    aggregate = False
    count = 1

    # Failure-rate (aka hazard) functions: return the probability
    # [0.0, 1.0) that this item will fail, given a lifetime of x
    @staticmethod
    def weibull(x, k, l):
        """Weibull failure function, with position l and shape k.  The
        mean of this distribution is l*Γ(1+1/k)."""
        return k/l * math.pow(x/l, k-1.0)

    @classmethod
    def name_for(cls, player=None, count=1):
        try:
            name = cls.name
        except AttributeError:
            name = cls.__name__.lower()
            
        if count > 1:
            try:
                return cls.name_plural % count
            except AttributeError:
                return name + "s"
        return name

    @classmethod
    def internal_name(cls):
        return cls.__module__.replace('wor.items.', '') + '.' + cls.__name__

    def __repr__(self):
        return '<Item: %s>' % self

    def __str__(self):
        return unicode(self).encode('utf8')

    def __unicode__(self):
        return self.name_for(count=self.count)

    def description(self):
        return getattr(self, 'desc', self.name_for())

    @classmethod
    def is_abstract(cls):
        return getattr(cls, '_%s__abstract' % cls.__name__, False)

    @classmethod
    def get_class(cls, name):
        """Obtain and cache an item class object by name"""
        items = Item.list_all_classes()
        return items[name]

    @classmethod
    def list_all_classes(cls):
        """Obtain a list of all item class names"""
        from wor import items
        try:
            return cls._item_cache
        except AttributeError:
            item_map = {}
            for k, v in items.__dict__.items():
                if isinstance(v, type) and issubclass(v, Item) and not v.is_abstract():
                    item_map[v.internal_name()] = v
            cls._item_cache = item_map
            return item_map

    def owner(self):
        """The notional owner of the item. For quantum items with
         multiple owners, this will be the owner that last touched it.

         """
        return self._owner

    def set_owner(self, obj):
        self._owner = obj

    def power(self, name):
        return getattr(self, name, 0)

    def destroy(self):
        """Destroy this item, recycling it if necessary"""
        #TODO

    def try_break(self):
        """Test this item for breakage, and return True if it broke"""
        if random.random() < self.break_profile(self.lifetime):
            # Then we broke. You may cry.
            self.destroy()
            return True

        return False

    def external_actions(self, player):
        """Retrieve the set of actions that can be performed on this
        object whilst held."""
        # Build system
        acts = []
        plans = makeable_plans(player, self)
        for p in plans:
            act = ActionMake(player, self, p)
            acts.append(act)
        return acts

    context_fields = ['description', 'count']

    def context_extra(self, context):    
        return {
            'name': unicode(self),
            'cls': self.internal_name()
        }

    def context_get_(self, context):
        """Return a dictionary of properties of this object, given the
        current authZ context"""
        ret = {}
        ret['id'] = db.id(self)
        ret['type'] = self.internal_name()

        auth = context.authz_item(self)
        if auth == Context.ADMIN:
            fields = Context.all_fields(self)
        elif auth == Context.OWNER:
            fields = ['name', 'damage', 'description']
        else:
            fields = ['name']

        return self.build_context(ret, fields)

    def merge(self, new_item):
        """Merge the given item with this item, if possible.  Return 
          True if the new item should be discarded, False otherwise"""
        return False
          
    def split(self, num_items):
        """Splits the given number of items from this item.  If this is 
           an aggregate, the split instance should be returned.  If 
           not, None will be returned"""
        return None


class AggregateItem(Item):
    """An item containing a number of identical objects.  Note that it 
       contains the underlying stuff in a conceptual sense only - rather 
       than containing 500 Gold objects, for example, it's simply a Gold 
       object with a 500 count"""
    __abstract = True
    aggregate = True

    def __init__(self, count=1):
        """Create a new AggregateItem with the given unit count."""
        super(AggregateItem, self).__init__()
        self.count = count

    def description(self):
        if self.count == 1:
            return getattr(self, 'desc', self.name_for())
        else:
            try:
                return self.desc_plural % self.count
            except AttributeError:
                return self.name_for()

    def merge(self, new_item):
        """Merge the given item with this item, if possible.  Return 
          True if the new item should be discarded, False otherwise"""

        # Make sure we're merging an object of the proper type
        #
        # TODO: Is this good, or do we need to support subclasses as 
        #       well?
        if self.internal_name() == new_item.internal_name():
            self.count += int(new_item.count)
            return True
        else:
            raise Util.WorError("Incompatible types (%s/%s) cannot be merged"
                                % (self.internal_name(), new_item.internal_name()))
        return False

    def split(self, num_items):
        """Splits the given number of items from this item.  If this is 
           an aggregate, the split instance should be returned.  If 
           not, None will be returned"""

        # Make sure we don't split more objects than we have.  If 
        # someone comes up with an aggregate that can be split into 
        # more instances than you originally had, then refactor this 
        # code.  I'll be in the corner trying to keep my head from 
        # exploding
        if self.count < num_items:
            raise InsufficientItemsException(
                "Cannot split %d items from an aggregate with only %d items"
                % (num_items, self.count))
        else:
            # Clone this object
            new_obj = self.__class__(num_items)

            # And adjust the counts accordingly
            self.count -= num_items

            return new_obj

        return None
