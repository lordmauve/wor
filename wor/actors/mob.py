from wor.actors.actor import Actor

from wor.actors.behaviour import BehaviourAimlessWander


class Mob(Actor):
    behaviour = BehaviourAimlessWander()

    def __init__(self, behaviour=None):
        super(Actor, self).__init__()
        if behaviour:
            self.behaviour = behaviour

    context_fields = ['id', 'hp', 'class_name']
    
    @classmethod
    def class_name(cls):
        try:
            return cls.taxonomy
        except AttributeError:
            mod = cls.__module__.replace('wor.', '')
            return mod + '.' + cls.__name__
