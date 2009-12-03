from django.db import models

class Actor(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=32)
    state = models.TextField() # This field type is a guess.
    x = models.IntegerField()
    y = models.IntegerField()
    layer = models.CharField(max_length=32)
    class Meta:
        db_table = u'actor'


class Account(models.Model):
    account_id = models.IntegerField(primary_key=True)
    username = models.CharField(unique=True, max_length=32)
    password = models.CharField(max_length=32)
    realname = models.CharField(max_length=64)
    email = models.CharField(max_length=64)

    def actors(self):
	return Actor.objects.filter(accountactor__account=self).distinct()

    class Meta:
        db_table = u'account'


class AccountActor(models.Model):
    account = models.ForeignKey(Account)
    actor = models.ForeignKey(Actor)
    class Meta:
        db_table = u'account_actor'


class ActorProperties(models.Model):
    actor = models.ForeignKey(Actor)
    key = models.TextField()
    type = models.TextField() # This field type is a guess.
    ivalue = models.IntegerField()
    fvalue = models.FloatField()
    tvalue = models.TextField()
    class Meta:
        db_table = u'actor_properties'


class ActorMessage(models.Model):
    id = models.IntegerField(primary_key=True)
    stamp = models.DecimalField(max_digits=20, decimal_places=6)
    actor_id = models.IntegerField()
    msg_type = models.TextField()
    message = models.TextField()
    class Meta:
        db_table = u'actor_message'


class Item(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=-1)
    state = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'item'


class ItemOwner(models.Model):
    item = models.ForeignKey(Item)
    owner_type = models.CharField(max_length=-1)
    owner_id = models.IntegerField()
    container = models.CharField(max_length=-1)
    class Meta:
        db_table = u'item_owner'


class ItemProperties(models.Model):
    item = models.ForeignKey(Item)
    key = models.TextField()
    type = models.TextField() # This field type is a guess.
    ivalue = models.IntegerField()
    fvalue = models.FloatField()
    tvalue = models.TextField()
    class Meta:
        db_table = u'item_properties'


class Location(models.Model):
    id = models.IntegerField(primary_key=True)
    x = models.IntegerField()
    y = models.IntegerField()
    layer = models.CharField(max_length=32)
    state = models.TextField() # This field type is a guess.
    overlay = models.IntegerField()

    def __unicode__(self):
	return 'Location <%d, %d, %r>' % (self.x, self.y, self.layer)

    class Meta:
        db_table = u'location'
	ordering = ['overlay']


class LocationProperties(models.Model):
    location = models.ForeignKey(Location)
    key = models.TextField()
    type = models.TextField() # This field type is a guess.
    ivalue = models.IntegerField()
    fvalue = models.FloatField()
    tvalue = models.TextField()
    class Meta:
        db_table = u'location_properties'


class LogRawAction(models.Model):
    id = models.IntegerField(primary_key=True)
    stamp = models.DateTimeField()
    request_id = models.TextField()
    action_id = models.TextField()
    action_name = models.TextField()
    parameters = models.TextField()
    class Meta:
        db_table = u'log_raw_action'
