from wor.actors.npc import HumanFemaleNPC
from cost import Cost
from wor.actions import trading


class Barmaid(HumanFemaleNPC):
    taxonomy = 'human.female.Barmaid'
    short_name = 'the Barmaid'
    full_name_format = '%s, the barmaid'

    buy_ale = trading.ActionBuy(
        item='drinks.Ale',
        cost=Cost(gp=3, ap=1),
    )
    buy_tequila = trading.ActionBuy(
        item='drinks.Tequila',
        cost=Cost(gp=2, ap=1),
    )
