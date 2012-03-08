from django.db import models

class Conference(models.Model):
    """
        set name and other info for conference
    """
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=False)

    sponsor_categories = models.ManyToManyField('sponsor.SponsorCategory')

    def __unicode__(self):
        return self.name

class Proposal(models.Model):
    """
        quick, un-ideal solution to collect proposals
    """
    CHOICES = (
        ('40min', '40 Minute Talk'),
        ('20min', '20 Minute Talk'),
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    speaker = models.ForeignKey('Speaker', null=True, related_name='proposals')
    proposal_name = models.CharField(max_length=255)
    proposal_length = models.CharField(max_length=255, choices=CHOICES)
    description = models.TextField()
    other = models.TextField(null=True, blank=True)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.proposal_name

class Speaker(models.Model):
    """
        speakers
    """
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    title = models.CharField(max_length=255, null=True, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.name

class Venue(models.Model):
    """
        set venue information for a conference
    """
    conference = models.OneToOneField('Conference', blank=True)
    name = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=10)
    country = models.CharField(max_length=2)
    description = models.TextField()