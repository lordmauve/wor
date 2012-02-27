from base import PersonalAction, LocalAction, SayField


class ActionSay(PersonalAction):
    def get_parameters(self):
        return [SayField('to_say')]

    caption = u"Say"

    def do(self, actor, target, to_say):
        for a in actor.loc().actors():
            a.message(to_say, 'say', actor)


class ActionWhisper(LocalAction):
    caption = u"Whisper"

    def get_parameters(self):
        return [SayField('to_say')]

    def do(self, actor, target, to_say):
        target.message(to_say, 'whisper', actor)
        return "You whisper to %s." % target


class ActionProd(LocalAction):
    caption = u"Prod"

    def do(self, actor, target):
        target.message('prods you.', 'action', actor)
        return "You prodded %s." % target

