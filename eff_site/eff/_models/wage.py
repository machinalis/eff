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
from customfields import MoneyField


class Wage(models.Model):
    date = models.DateField()
    amount_per_hour = MoneyField()
    user = models.ForeignKey(User)

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.id:
            try:
                Wage.objects.get(date=self.date, user=self.user)
                raise ValidationError('Already exists this Date for this User')
            except Wage.DoesNotExist:
                pass

    def __unicode__(self):
        return u'[%s] %s : %s' % (self.id, self.date, self.amount_per_hour)

    class Meta:
        app_label = 'eff'
        get_latest_by = 'date'
        ordering = ['date', 'user']
        unique_together = (('user', 'date'))
