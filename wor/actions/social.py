from base import *


class ActionSay(Action):
    def get_parameters(self):
        return [SayField('to_say')]

    def get_caption(self):
        return u"Say"

    def get_uid(self):
        return 'say'

    def action(self, to_say):
        for a in self.actor.loc().actors():
            a.message(to_say, 'say', self.actor)


class ActionProd(TargettedAction):
    caption = u"Prod %s"

    def action(self):
        self.target.message('prods you.', 'action', self.actor)
        return "You prodded %s." % self.target

