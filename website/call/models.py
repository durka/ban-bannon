from django.db import models

class Politician(models.Model):
    HAS_NOT_SAID = 'N'
    SUPPORTS = 'S'
    DENOUNCES = 'D'
    HOUSE = 'H'
    SENATE = 'S'
    zipcode = models.CharField(max_length=5)
    district_or_class = models.PositiveSmallIntegerField()
    chamber = models.CharField(max_length=1,
                               choices=[(HOUSE, 'House of Representatives'),
                                        (SENATE, 'Senate')])
    position = models.CharField(max_length=1,
                                choices=[(HAS_NOT_SAID, 'Has not said'),
                                         (SUPPORTS, 'Supports'),
                                         (DENOUNCES, 'Denounces')],
                                default=HAS_NOT_SAID)
    shown_to_all = models.BooleanField(default=False)
    extra_phones = models.ForeignKey('Phone', null=True, blank=True)
    script = models.TextField(default=None, null=True, blank=True)

    def __str__(self):
        return '%s-%s %s' % (self.zipcode, self.district_or_class, self.chamber)

class Phone(models.Model):
    number = models.CharField(max_length=10)
    desc = models.TextField()

    def __str__(self):
        return '%s: (%s) %s-%s' % (self.desc, self.number[0:3], self.number[3:6], self.number[6:])

