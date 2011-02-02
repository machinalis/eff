from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta, datetime
from avg_hours import AvgHours
from django.db.models import permalink, signals

from project import Project, ProjectAssoc
from log import TimeLog

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)

    personal_email = models.EmailField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    address = models.CharField(max_length=80, blank=True)
    phone_number = models.CharField(max_length=40, blank=True, null=True)

    projects = models.ManyToManyField(Project, verbose_name=u'Projects', through=ProjectAssoc)

    class Meta:
        app_label = 'eff'
        permissions = (('view_billable',
                        'Can view the percetage of billable hours'),
                       ('view_wage',
                        'Can view the salary per hour of a user'),)

    def __unicode__(self):
        return u'%s (%s)' % (self.user.get_full_name(), self.user.username)
    
    def get_avg_hours_for(self, ndate):
        try:
            hours = self.user.avghours_set.filter(date__lte=ndate).latest().hours
        except:
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
            new_avg_hour = AvgHours(date=new_date, hours=hours,user=self.user)
            new_avg_hour.save()
        else:
            raise ValueError, "Negative value for hours"

    def update_avg_hour(self, udate, hours):
        if hours >= 0:
            try:
                update_date = self.user.avghours_set.get(date=udate)
            except:
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

    def get_worked_hours (self, from_date, to_date):
        return self.__sum_hours(lambda i, p: i.hours_per_project(p, from_date, to_date), to_date)

    def get_worked_hours_per_day (self, a_date):
        return self.__sum_hours(lambda i, p: i.hours_per_project_a_day(p, a_date), a_date)

    def billable_hours (self, from_date, to_date):
        return self.__sum_hours(lambda i, p: i.billable_hours(p, from_date, to_date), to_date)

    def billable_hours_a_day (self, a_date):
        return self.__sum_hours(lambda i, p: i.billable_hours_a_day(p, a_date), a_date)

    def __sum_hours (self, f, a_date):
        # Unify sums to avoid interval ending issues! (and code duplication)
        hours = round(f(TimeLog, self), 2)
        return hours

    def percentage_hours_worked(self, from_date, to_date):
        wh = self.get_worked_hours(from_date, to_date)
        th = self.num_loggable_hours(from_date, to_date)
        if th == 0:
            raise ValueError, 'No loggable hours'
        else:
            return round((wh/th)*100, 2)

    def percentage_billable_hours (self, from_date, to_date):
        bh = self.billable_hours(from_date, to_date)
        th = self.num_loggable_hours(from_date, to_date)
        if th == 0:
            raise ValueError, 'No loggable hours'
        else:
            return round((bh/th)*100, 2)

    def _wrap_user(self, *args):
        # I <3 dynamic typing :-D
        # ToDo: Fix this. 
        self.user.login = self.user.username
        return self.user
                

    def report(self, from_date, to_date, project=None):
        report = list(TimeLog.report(self, from_date, to_date, project))

        #Ordenamos por fecha
        report.sort(lambda x,y: cmp(datetime(x[4].year, x[4].month, x[4].day),\
                                        datetime(y[4].year, y[4].month, y[4].day)))
        return report

    def get_absolute_url(self):
        return ('profiles_profile_detail', (), { 'username': self.user.username })
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
        profile = UserProfile( user = instance )
        profile.save()

signals.post_save.connect(create_profile_for_user, sender=User)

#-------------------------------------------------------------------------------
