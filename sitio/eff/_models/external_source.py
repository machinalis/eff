from django.db import models
from user_profile import UserProfile


class ExternalId(models.Model):
    login = models.CharField(max_length=100)
    source = models.ForeignKey('ExternalSource', null=True)
    userprofile = models.ForeignKey(UserProfile)

    class Meta:
        app_label = 'eff'

    def __unicode__(self):
        return u'%s' % (self.login,)

class ExternalSource(models.Model):
    name = models.CharField(max_length=200)
    fetch_url = models.CharField(max_length=500, blank=True)
    username = models.CharField(max_length=50, blank=True)
    password = models.CharField(max_length=50, blank=True)
    csv_directory = models.CharField(max_length=100, blank=True)
    csv_filename = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        app_label = 'eff'

    def __unicode__(self):
        return u'%s' % (self.name,)
