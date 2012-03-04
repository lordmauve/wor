import random
from functools import partial
from pkg_resources import resource_string

from wor.actors.mob import Mob



def random_name(resource):
    """Return a random name from the resource name given"""
    names = resource_string(__name__, resource)
    return random.choice(names.splitlines())


random_male_name = partial(random_name, 'names/male-names.txt')
random_female_name = partial(random_name, 'names/female-names.txt')
random_surname = partial(random_name, 'names/surnames.txt')


class NPC(Mob):
    def __init__(self, name, behaviour):
        super(NPC, self).__init__(behaviour)
        self.name = name

    def full_name(self):
        return self.full_name_format % self.name

    context_fields = ['id', 'hp', 'class_name', 'short_name', 'full_name']

    def context_extra(self, player):
        ctx = {}
        ctx['actions'] = [a.context_get(player) for a in self.external_actions(player)]
        return ctx


class HumanNPC(NPC):
    MALE = 0
    FEMALE = 1

    def __init__(self, behaviour=None, gender=None):
        """Construct a new human NPC.

        If gender is not given, it is picked at random.
        """
        if gender is None:
            gender = random.randint(0, 1)
        self.gender = gender

        if gender == HumanNPC.MALE:
            given = random_male_name()
        else:
            given = random_female_name()
        family = random_surname()

        super(HumanNPC, self).__init__(given + ' ' + family, behaviour)


class HumanMaleNPC(HumanNPC):
    """Subclass of NPC that is explicitly male."""
    def __init__(self, behaviour=None):
        super(HumanMaleNPC, self).__init__(behaviour, gender=HumanNPC.MALE)


class HumanFemaleNPC(HumanNPC):
    """Subclass of NPC that is explicitly female."""
    def __init__(self, behaviour=None):
        super(HumanMaleNPC, self).__init__(behaviour, gender=HumanNPC.FEMALE)

