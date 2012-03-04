from base import PersonalAction, LocalAction, SayField


class SocialAction(LocalAction):
    """Base class for actions can only be performed on another actor.
    
    A SocialAction can only be performed if both actors are in the same
    location.
    """
    def valid(self, actor, target):
        return actor is not target and super(SocialAction, self).is_valid()


class ActionSay(PersonalAction):
    """Say something aloud."""

    def get_parameters(self):
        return [SayField('to_say')]

    caption = u"Say"

    def do(self, actor, target, to_say):
        for a in actor.loc().actors():
            a.message(to_say, 'say', actor)


class ActionWhisper(SocialAction):
    """Whisper something to another actor."""

    caption = u"Whisper"

    def get_parameters(self):
        return [SayField('to_say')]

    def do(self, actor, target, to_say):
        target.message(to_say, 'whisper', actor)
        return "You whisper to %s." % target


class ActionProd(SocialAction):
    """Prod another actor.

    The target actor will be informed that they were prodded.
    """
    caption = u"Prod"

    def do(self, actor, target):
        target.message('prods you.', 'action', actor)
        return "You prodded %s." % target

