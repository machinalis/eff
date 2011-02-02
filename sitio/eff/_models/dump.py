from django.db import models
#from external_source import ExternalSource

class Dump(models.Model):
    date = models.DateField()
    creator = models.CharField(max_length=100)
    source = models.ForeignKey('ExternalSource', null=True)

    class Meta:
        app_label = 'eff'

    def __unicode__(self):
        return u'Dump - source: %s, created by: %s, date: %s' % (self.source,
                                                                 self.creator,
                                                                 self.date)
