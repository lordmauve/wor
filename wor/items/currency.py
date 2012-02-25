#coding: utf8

from base import Item, AggregateItem

class GoldPiece(AggregateItem):
    name = 'denarius'
    name_plural = 'denarii'
    group = "Currency"

    def __unicode__(self):
        librae = self.count // 240
        solidi = (self.count % 240) // 20
        denarii = self.count % 20
        if librae:
            return u"£%d %ds %dd" % (librae, solidi, denarii)
        elif solidi:
            return u"%ds %dd" % (solidi, denarii)
        elif denarii:
            return u"%dd" % denarii
