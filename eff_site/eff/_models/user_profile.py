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
from datetime import timedelta, datetime
from avg_hours import AvgHours
from django.db.models import permalink, signals
from django.core.exceptions import MultipleObjectsReturned

from project import Project, ProjectAssoc
from log import TimeLog
from decimal import Decimal


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)

    personal_email = models.EmailField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    address = models.CharField(max_length=80, blank=True)
    phone_number = models.CharField(max_length=40, blank=True, null=True)

    projects = models.ManyToManyField(Project, verbose_name=u'Projects',
        through=ProjectAssoc)

    class Meta:
        app_label = 'eff'
        permissions = (('view_billable',
                        'Can view the percetage of billable hours'),
                       ('view_wage',
                        'Can view the salary per hour of a user'),)
        ordering = ['user__first_name']

    def __unicode__(self):
        return u'%s (%s)' % (self.user.get_full_name(), self.user.username)

    def get_avg_hours_for(self, ndate):
        try:
            hours = self.user.avghours_set.filter(
                date__lte=ndate).latest().hours
        except AvgHours.DoesNotExist:
            hours = 0
        return hours

    def num_loggable_hours(self, from_date, to_date):

        start_hours = self.get_avg_hours_for(from_date)
        lista_ah = list(self.user.avghours_set.filter(date__gt=from_date,
                                                      date__lte=to_date))
        delta = timedelta(days=1)
        num = 0

        hours = start_hours
        while(from_date <= to_date):
            if lista_ah:
                if from_date == lista_ah[0].date:
                    hours = lista_ah[0].hours
                    from_date = lista_ah.pop(0).date
            if 1 <= from_date.isoweekday() <= 5:
                num += hours
            from_date += delta

        return num

    def add_avg_hours(self, new_date, hours):
        if hours >= 0:
            new_avg_hour = AvgHours(date=new_date, hours=hours, user=self.user)
            new_avg_hour.validate_unique()
            new_avg_hour.save()
        else:
            raise ValueError, "Negative value for hours"

    def update_avg_hour(self, udate, hours):
        if hours >= 0:
            try:
                update_date = self.user.avghours_set.get(date=udate)
            except (AvgHours.DoesNotExist, MultipleObjectsReturned):
                raise ValueError, "AvgHour inexistent"
            else:
                update_date.hours = hours
                update_date.save()
        else:
            raise ValueError, "Negative value for hours"

    def is_active(self, from_date, to_date):
        delta = timedelta(days=1)
        while to_date >= from_date:
            if self.get_avg_hours_for(to_date) > 0:
                return True
            to_date -= delta

    def get_worked_hours(self, from_date, to_date):
        return self.__sum_hours(
            lambda i, p: i.hours_per_project(p, from_date, to_date), to_date)

    def get_worked_hours_per_day(self, a_date):
        return self.__sum_hours(
            lambda i, p: i.hours_per_project_a_day(p, a_date), a_date)

    def billable_hours(self, from_date, to_date):
        return self.__sum_hours(
            lambda i, p: i.billable_hours(p, from_date, to_date), to_date)

    def billable_hours_a_day(self, a_date):
        return self.__sum_hours(
            lambda i, p: i.billable_hours_a_day(p, a_date), a_date)

    def __sum_hours(self, f, a_date):
        # Unify sums to avoid interval ending issues! (and code duplication)
        hours = f(TimeLog, self)
        if (type(hours) != Decimal) and (hours == 0):
            hours = Decimal(hours)
        assert hours.__class__ == Decimal, "The variable hours is not a Decimal"
        return hours

    def percentage_hours_worked(self, from_date, to_date):
        wh = self.get_worked_hours(from_date, to_date)
        th = self.num_loggable_hours(from_date, to_date)
        if th == 0:
            raise ValueError, 'No loggable hours'
        else:
            # For total values of this, see eff.utils.DataTotal
            # phw must be a Decimal
            phw = ((wh / th) * 100).quantize(Decimal('.00'))
            return phw

    def percentage_billable_hours(self, from_date, to_date):
        bh = self.billable_hours(from_date, to_date)
        th = self.num_loggable_hours(from_date, to_date)
        if th == 0:
            raise ValueError, 'No loggable hours'
        else:
            # For total values of this, see eff.utils.DataTotal
            # pbh must be a Decimal
            pbh = ((bh / th) * 100).quantize(Decimal('.00'))
            return pbh

    def _wrap_user(self, *args):
        # I <3 dynamic typing :-D
        # ToDo: Fix this.
        self.user.login = self.user.username
        return self.user

    def report(self, from_date, to_date, project=None):
        report = list(TimeLog.report(self, from_date, to_date, project))

        #Ordenamos por fecha
        report.sort(lambda x, y: cmp(datetime(x[4].year, x[4].month, x[4].day),\
                                    datetime(y[4].year, y[4].month, y[4].day)))
        return report

    def get_absolute_url(self):
        return ('profiles_profile_detail', (), {'username': self.user.username})
    get_absolute_url = permalink(get_absolute_url)

    def projects(self, from_date, to_date):
        projects = TimeLog.user_projects(self, from_date, to_date)
        return projects


#----------------------- Para manejo de seniales -------------------------------

def create_profile_for_user(sender, instance, signal, *args, **kwargs):
    try:
        UserProfile.objects.get(user=instance)
    except UserProfile.DoesNotExist, e:
        #si no existe, creamos el profile para el usuario
        profile = UserProfile(user=instance)
        profile.save()

signals.post_save.connect(
    create_profile_for_user, sender=User,
    dispatch_uid='eff._models.user_profile.create_profile_for_user')

#-------------------------------------------------------------------------------
