from django.db import models

class Politician(models.Model):
    HAS_NOT_SAID = 'N'
    SUPPORTS = 'S'
    DENOUNCES = 'D'
    HOUSE = 'H'
    SENATE = 'S'
    chamber = models.CharField(max_length=1,
                               choices=[(HOUSE, 'House of Representatives'),
                                        (SENATE, 'Senate')])
    state = models.CharField(max_length=2)
    district_or_class = models.PositiveSmallIntegerField(default=None)
    position = models.CharField(max_length=1,
                                choices=[(HAS_NOT_SAID, 'Has not said'),
                                         (SUPPORTS, 'Supports'),
                                         (DENOUNCES, 'Denounces')],
                                default=HAS_NOT_SAID)
    shown_to_all = models.BooleanField(default=False)
    extra_phones = models.ForeignKey('Phone', null=True)

    def __str__(self):
        return '%s-%s-%d' % (self.chamber, self.state, self.district_or_class)

class Phone(models.Model):
    number = models.CharField(max_length=10)
    desc = models.TextField()

    def __str__(self):
        return '%s: (%s) %s-%s' % (self.desc, self.number[0:3], self.number[3:6], self.number[6:])

