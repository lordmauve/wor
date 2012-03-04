from .base import AggregateItem
from wor.actions.inventory import ConsumeAction
from wor.cost import Cost


class Ingredient(AggregateItem):
    group = "Food"

    eat = ConsumeAction(
        label=u'Eat',
        cost=Cost(ap=1, hp=-5)
    )


class Mushroom(Ingredient):
    name = 'a mushroom'
    name_plural = '%d mushrooms'


class Rosemary(Ingredient):
    name = 'some rosemary'
    name_plural = '%d handfuls of rosemary'


class Salmon(Ingredient):
    name = 'a salmon'
    name_plural = '%d salmon'

    eat = ConsumeAction(
        label=u'Eat',
        cost=Cost(ap=1, hp=-10),
        message='Mmm... sashimi.'
    )


class Perch(Ingredient):
    name = 'a perch'
    name_plural = '%d perch'

    eat = ConsumeAction(
        label=u'Eat',
        cost=Cost(ap=1, hp=-6),
        message='Bleh... raw perch.'
    )


class Carp(Ingredient):
    name = 'a carp'
    name_plural = '%d carp'

    eat = ConsumeAction(
        label=u'Eat',
        cost=Cost(ap=1, hp=-6),
        message='Raw carp... is not nice.'
    )
