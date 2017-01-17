from django.db import models

class GetOrNoneManager(models.Manager):
    """Adds get_or_none method to objects
    """
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None

class Campaign(models.Model):
    name = models.CharField(max_length=20, unique=True)
    hashtag = models.CharField(max_length=100)
    action = models.TextField(default=None, blank=True, null=True)
    checker = models.CharField(max_length=100, default=None, blank=True, null=True)
    include_senators = models.BooleanField(default=True)
    include_representatives = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Position(models.Model):
    HAS_NOT_SAID = 'N'
    SUPPORTS = 'S'
    DENOUNCES = 'D'

    politician = models.ForeignKey('Politician')
    campaign = models.ForeignKey('Campaign')
    position = models.CharField(max_length=1,
                                choices=[(HAS_NOT_SAID, 'Has not said'),
                                         (SUPPORTS,     'Supports'    ),
                                         (DENOUNCES,    'Denounces'   )],
                                default=HAS_NOT_SAID)
    script = models.TextField(default=None, blank=True)

    def __str__(self):
        return '%s: %s %s' % (self.politician, self.position, self.campaign)

class Politician(models.Model):
    objects = GetOrNoneManager()

    HOUSE = 'H'
    SENATE = 'S'

    zip_or_state = models.CharField(max_length=5)
    district_or_class = models.PositiveSmallIntegerField()
    chamber = models.CharField(max_length=1,
                               choices=[(HOUSE, 'House of Representatives'),
                                        (SENATE, 'Senate')])
    leadership_role = models.CharField(max_length=255, blank=True)
    shown_to_all = models.ManyToManyField(Campaign, blank=True)

    def __str__(self):
        return '%s-%s %s' % (self.zip_or_state, self.district_or_class, self.chamber)

class Phone(models.Model):
    number = models.CharField(max_length=10)
    desc = models.TextField()
    politician = models.ForeignKey('Politician')

    def __str__(self):
        return '%s: (%s) %s-%s' % (self.desc, self.number[0:3], self.number[3:6], self.number[6:])

