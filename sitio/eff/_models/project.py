from django.db import models

class ProjectAssoc(models.Model):
    project = models.ForeignKey('Project')
    member = models.ForeignKey('UserProfile')
    client_rate = models.FloatField()
    user_rate = models.FloatField()
    from_date = models.DateField()
    to_date = models.DateField(null=True, blank=True)

    class Meta:
        app_label = 'eff'
        verbose_name = 'Project-User Association'

    def __unicode__(self):
        return u"%s in project %s, from %s %s with rate of %s and client rate %s " % \
            (self.member, self.project, self.from_date, self.to_date and ("to %s" % self.to_date) or "until today", 
             self.user_rate, self.client_rate, )


class Project(models.Model):
    name = models.CharField(max_length=200)
    billable = models.BooleanField(default=False)
    external_id = models.CharField(max_length=100, blank=True)
    client = models.ForeignKey('Client')
    members = models.ManyToManyField('UserProfile', verbose_name=u'Members', through=ProjectAssoc)

    billing_type = models.CharField(max_length=8, 
                                    choices=(('FIXED','Fixed Price'),('HOUR', 'Per Hour')), 
                                    default='HOUR')
    fixed_price = models.FloatField(blank=True, null=True)

    class Meta:
        app_label = 'eff'

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.client.name)

    def get_external_source(self):
        return self.client.external_source
    
