from Plan import Plan, plans
from Alignment import Alignment

plans.append(Plan(
    name        = "haymaker",
    materials    = { 'Punch': 1 },
    makes        = { 'Haymaker': 1 },
    ap            = 1,
    ap10        = 8,
    align        = Alignment.FIRE
    ))
