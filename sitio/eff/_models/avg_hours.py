# Copyright 2009 - 2011 Machinalis: http://www.machinalis.com/
#
# This file is part of Eff.
#
# Eff is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Eff is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Eff.  If not, see <http://www.gnu.org/licenses/>.

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
