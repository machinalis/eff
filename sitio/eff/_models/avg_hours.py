from django.db import models
from django.contrib.auth.models import User

class AvgHours(models.Model):
    date = models.DateField()
    hours = models.FloatField()
    user = models.ForeignKey(User)

    def __unicode__(self):
        return u'%s - %s : %s '% (self.user.get_full_name(),
                                 self.date,
                                 self.hours)

    def save(self):
        qs = AvgHours.objects.filter(date=self.date, user=self.user)
        if qs:
            if self.id:
                # self viene de la db
                this_id = int(self.id)
            else:
                # self es nuevo
                this_id = object() # marker
            other_id = AvgHours.objects.get(date=self.date, user=self.user).id
            if this_id != other_id:
                raise ValueError, "Date already exists"
        return super(AvgHours, self).save()

    class Meta:
        app_label = 'eff'
        get_latest_by = 'date'
        ordering = ['date','user']
        unique_together=(('user','date'),)
