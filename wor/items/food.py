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
