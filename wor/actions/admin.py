from .base import Action


class AdminAction(Action):
    """An action that can only be performed by an immortal."""
    def is_valid(self, player, target):
        return getattr(player, 'immortal', False)


class ActionSpawn(AdminAction):
    cost = None
    group = 'spawn'
    caption = u"Spawn %s"
    mob = None

    def get_caption(self, target):
        return self.caption % self.mob.class_name() 
    
    def do(self, actor, target):
        mob = self.mob()
        world = target.region.world
        world.spawn_actor(mob, target.pos)
        return '%s spawned at %s.' % (mob, target.pos)
