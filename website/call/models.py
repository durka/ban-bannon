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
    state = models.CharField(max_length=2, choices=[('AL', 'Alabama'),
                                                    ('AK', 'Alaska'),
                                                    ('AZ', 'Arizona'),
                                                    ('AR', 'Arkansas'),
                                                    ('CA', 'California'),
                                                    ('CO', 'Colorado'),
                                                    ('CT', 'Connecticut'),
                                                    ('DE', 'Delaware'),
                                                    ('FL', 'Florida'),
                                                    ('GA', 'Georgia'),
                                                    ('HI', 'Hawaii'),
                                                    ('ID', 'Idaho'),
                                                    ('IL', 'Illinois'),
                                                    ('IN', 'Indiana'),
                                                    ('IA', 'Iowa'),
                                                    ('KS', 'Kansas'),
                                                    ('KY', 'Kentucky'),
                                                    ('LA', 'Louisiana'),
                                                    ('ME', 'Maine'),
                                                    ('MD', 'Maryland'),
                                                    ('MA', 'Massachusetts'),
                                                    ('MI', 'Michigan'),
                                                    ('MN', 'Minnesota'),
                                                    ('MS', 'Mississippi'),
                                                    ('MO', 'Missouri'),
                                                    ('MT', 'Montana'),
                                                    ('NE', 'Nebraska'),
                                                    ('NV', 'Nevada'),
                                                    ('NH', 'New Hampshire'),
                                                    ('NJ', 'New Jersey'),
                                                    ('NM', 'New Mexico'),
                                                    ('NY', 'New York'),
                                                    ('NC', 'North Carolina'),
                                                    ('ND', 'North Dakota'),
                                                    ('OH', 'Ohio'),
                                                    ('OK', 'Oklahoma'),
                                                    ('OR', 'Oregon'),
                                                    ('PA', 'Pennsylvania'),
                                                    ('RI', 'Rhode Island'),
                                                    ('SC', 'South Carolina'),
                                                    ('SD', 'South Dakota'),
                                                    ('TN', 'Tennessee'),
                                                    ('TX', 'Texas'),
                                                    ('UT', 'Utah'),
                                                    ('VT', 'Vermont'),
                                                    ('VA', 'Virginia'),
                                                    ('WA', 'Washington'),
                                                    ('WV', 'West Virginia'),
                                                    ('WI', 'Wisconsin'),
                                                    ('WY', 'Wyoming')])
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

