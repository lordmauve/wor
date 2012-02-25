import random

class BehaviourStatic(object):    
    def update(self, mob):
        print "Keeping", mob.full_name(), "stationary"


class BehaviourAimlessWander(object):    
    def update(self, mob):
        l = mob.loc()
        dirs = []
        # build a list of permissible directions around mob
        for i in range(0, 6):
            n = l.local_directions_name[i]
            if l.could_go(mob, n):
                dirs.append(i)

        # select one at random
        d = random.choice(dirs)
        dest = l.local_directions[d](l)
        print "Moving", mob.full_name(), "to", dest
        mob.position = dest.pos



