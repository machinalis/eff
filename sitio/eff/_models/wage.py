from django.db import models
from django.contrib.auth.models import User


class Wage(models.Model):
    date = models.DateField()
    amount_per_hour = models.FloatField()
    user = models.ForeignKey(User)

    def __unicode__(self):
        return u'[%s] %s : %s'% (self.id, self.date, self.amount_per_hour)

    def save(self):
        qs = Wage.objects.filter(date=self.date, user=self.user)
        if qs:
            if self.id:
                # self viene de la db
                this_id = int(self.id)
            else:
                # self es nuevo
                this_id = object() # marker
            other_id = Wage.objects.get(date=self.date, user=self.user).id
            if this_id != other_id:
                raise ValueError, "Date already exists"
        return super(Wage, self).save()

    class Meta:
        app_label = 'eff'
        get_latest_by = 'date'
        ordering = ['date', 'user']
        unique_together = (('user', 'date'))
