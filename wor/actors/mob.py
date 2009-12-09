from wor.actors.actor import Actor

from wor.actors.behaviour import BehaviourAimlessWander


class Mob(Actor):
	behaviour = BehaviourAimlessWander()

	def __init__(self, behaviour=None):
		super(Actor, self).__init__()
		if behaviour:
			self.behaviour = behaviour

	context_fields = ['id', 'hp', 'class_name']
	
	def class_name(self):
		if self.taxonomy:
			return self.taxonomy	
		mod = self.__class__.__module__.replace('wor.', '')
		return mod + '.' + self.__class__.__name__
