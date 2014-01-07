from wor.actors.npc import HumanNPC, HumanFemaleNPC
from wor.cost import Cost
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


class Trader(HumanNPC):
    taxonomy = 'human.Trader'
    short_name = 'a Trader'
    full_name_format = '%s, a Trader'

    buy_bucket = trading.ActionBuy(
        item='tools.Bucket',
        cost=Cost(gp=12, ap=1),
    )
    buy_spade = trading.ActionBuy(
        item='tools.Spade',
        cost=Cost(gp=20, ap=1),
    )
    buy_pickaxe = trading.ActionBuy(
        item='tools.PickAxe',
        cost=Cost(gp=35, ap=1),
    )
    buy_rod = trading.ActionBuy(
        item='tools.FishingRod',
        cost=Cost(gp=25, ap=1),
    )
