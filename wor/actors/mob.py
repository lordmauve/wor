from wor.actors.actor import Actor

from wor.actors.behaviour import BehaviourStatic

class Mob(Actor):
	behaviour = BehaviourStatic()

	def __init__(self, behaviour):
		super(Actor, self).__init__()
		self.behaviour = behaviour

	context_fields = ['id', 'hp', 'class_name']
	
	def class_name(self):
		if self.taxonomy:
			return self.taxonomy	
		mod = self.__class__.__module__.replace('wor.', '')
		return mod + '.' + self.__class__.__name__
