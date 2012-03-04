from .base import Item, AggregateItem


class Bucket(AggregateItem):
    name = 'a bucket'
    name_plural = '%d buckets'


class BucketOfWater(Bucket):
    name = 'a bucket of water'
    name_plural = '%d buckets of water'


class BucketOfMilk(Bucket):
    name = 'a bucket of milk'
    name_plural = '%d buckets of milk'


class BucketOfSeaWater(Bucket):
    name = 'a bucket of sea water'
    name_plural = '%d buckets of sea water'


class Spade(Item):
    name = 'a spade'


class PickAxe(Item):
    name = 'a pickaxe'
