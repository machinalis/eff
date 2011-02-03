# -*- coding: utf-8 -*-
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
from project import Project, ProjectAssoc
from django.db.models import Sum, Min

from dump import Dump

from django.db.models import Q
from datetime import timedelta

class TimeLog(models.Model):

    date = models.DateField()
    project = models.ForeignKey(Project)
    task_name = models.CharField(max_length=500, blank=True)
    user = models.ForeignKey(User)
    hours_booked = models.FloatField()
    description = models.TextField(blank=True)

    dump = models.ForeignKey(Dump)

    class Meta:
        app_label = 'eff'

    def __unicode__(self):
        return u'[%s, %s, %s, %s]' % (self.date, self.project, self.user, self.hours_booked)


    @classmethod
    def _query(klass, user, from_date, to_date, project=None, billable=False):
        kwargs = dict(date__gte=from_date,
                      date__lte=to_date,
                      user__username=user.user.username) # it's an instance of UserProfile

        if not (project is None):
            kwargs['project'] = project

        if billable:
            kwargs['project__billable'] = True

        return klass.objects.filter(**kwargs)

    @classmethod
    def hours_per_project(klass, user, from_date, to_date, project=None):
        qset = klass._query(user, from_date, to_date, project)
        return sum(log.hours_booked for log in qset)

    @classmethod
    def user_projects(self, user, from_date, to_date):
        return Project.objects.filter(timelog__user__username=user.user.username, 
                                      timelog__date__gte=from_date, 
                                      timelog__date__lte=to_date).distinct()

    @classmethod
    def _group_by_project(klass, qset):
        last = None
        acc = 0
        qset = qset.order_by('project')

        for item in qset:

            if (last is None):
                last = item.project
                acc = item.hours_booked

            elif (last == item.project):
                acc += item.hours_booked

            elif (last != item.project):
                yield (last, '', acc)
                acc = item.hours_booked
                last = item.project

        if last is not None:
            yield (last, '', acc)
        else:
            yield None

    @classmethod
    def hours_grouped_by_project(klass, user, from_date, to_date):
        qset = klass._query(user, from_date, to_date, None)
        return klass._group_by_project(qset)

    @classmethod
    def hours_grouped_by_project_with_rates(klass, user, from_date, to_date):
        user_projects = klass.user_projects(user, from_date, to_date)
        # Discard project associations out of the period
        projassoc = ProjectAssoc.objects.filter(Q(member__user__username=user.user.username),
                                                Q(project__in=user_projects),
                                                ~Q(from_date__gt=to_date),
                                                ~Q(to_date__lt=from_date))

        start_dates = projassoc.values('project').annotate(Min("from_date"))
        projects_dates = {}
        for m_dates in start_dates:
            project = Project.objects.get(id=m_dates['project'])
            d_date = m_dates['from_date__min']
            if d_date > from_date: d_date = from_date
            next_dates = projassoc.filter(Q(project=project), Q(member__user__username=user.user.username), 
                                          Q(from_date__gt=d_date) | Q(to_date__gt=d_date)).order_by("from_date")
            f_dates = [pa.from_date for pa in next_dates if pa.from_date > d_date]
            t_dates = [pa.to_date for pa in next_dates if pa.to_date is not None and pa.to_date > d_date]
            dates = f_dates + t_dates
            dates = filter(lambda d: d > from_date and d < to_date, dates)
            projects_dates[project] = [from_date] + sorted(dates) + [to_date]

        # Get the rates
        rates = []
        for project, dates in projects_dates.items():
            project_rates = []
            while len(dates)>0:
                d1 = dates.pop(0) 
                try:
                    d2 = dates[0]
                except IndexError:
                    args = (Q(member__user__username=user.user.username), 
                            Q(project=project), 
                            Q(from_date__lte=d1), 
                            Q(to_date__isnull=True))
                else:
                    args = (Q(member__user__username=user.user.username), 
                            Q(project=project), 
                            Q(from_date__lte=d1), 
                            Q(to_date__gte=d2) | 
                            Q(to_date__isnull=True))
                assocs = projassoc.filter(*args).order_by("-from_date")
                if assocs:
                    if project_rates: 
                        # Two project associations can't overlap
                        if project_rates[len(project_rates)-1][1]==d1:
                            project_rates[len(project_rates)-1][1] = d1 - timedelta(days=1)
                    project_rates.append([d1, d2, assocs[0].user_rate])

            project_rates = join_dups(project_rates)
            rates.append((project, project_rates))

        # Generate hours with rates according to project associations periods
        t_hours = []
        for project, rate_list in rates:
            for rate in rate_list:
                hours = klass.objects.filter(date__gte=rate[0],
                                             date__lte=rate[1],
                                             project=project,
                                             user__username=user.user.username)
                hours = hours.values('project').annotate(Sum("hours_booked"))
                if hours:
                    hours = hours[0]
                    repeated = filter(lambda d: d['project']==project.id and d['rate']==rate[2], 
                                      t_hours)
                    if repeated:
                        i = t_hours.index(repeated[0])
                        t_hours[i]['hours_booked__sum']+=hours['hours_booked__sum']
                    elif hours:
                        hours['rate'] = rate[2]
                        t_hours.append(hours)

        return map(lambda d: (Project.objects.get(id=d['project']), '', d['hours_booked__sum'], d['rate']), 
                   t_hours)

    @classmethod
    def project_hours(self, project, from_date, to_date):
        hours = self.objects.filter(date__gte=from_date,
                                    date__lte=to_date,
                                    project=project)
        hours = hours.values('user__username').annotate(Sum("hours_booked"))
        return hours

    @classmethod
    def project_hours_grouped_by_rate(self, project, from_date, to_date):
        # Discard project associations out of the period
        projassoc = ProjectAssoc.objects.filter(Q(project=project), 
                                                ~Q(from_date__gt=to_date), 
                                                ~Q(to_date__lt=from_date))

        start_dates = projassoc.values('member__user').annotate(Min("from_date"))
        users_dates = {}
        for m_dates in start_dates:
            user = User.objects.get(id=m_dates['member__user'])
            d_date = m_dates['from_date__min']
            if d_date > from_date: d_date = from_date
            next_dates = projassoc.filter(Q(project=project), Q(member__user=user), 
                                          Q(from_date__gt=d_date) | Q(to_date__gt=d_date)).order_by("from_date")
            f_dates = [pa.from_date for pa in next_dates if pa.from_date > d_date]
            t_dates = [pa.to_date for pa in next_dates if pa.to_date is not None and pa.to_date > d_date]
            dates = f_dates + t_dates
            dates = filter(lambda d: d > from_date and d < to_date, dates)
            users_dates[user] = [from_date] + sorted(dates) + [to_date]

        
        # Get the rates
        rates = []
        for user, dates in users_dates.items():
            user_rates = []
            while len(dates) > 0:
                d1 = dates.pop(0) 
                try:
                    d2 = dates[0]
                except IndexError:                  
                    args = (Q(member__user=user), 
                            Q(project=project), 
                            Q(from_date__lte=d1), 
                            Q(to_date__isnull=True))
                else:
                    args = (Q(member__user=user), 
                            Q(project=project), 
                            Q(from_date__lte=d1), 
                            Q(to_date__gte=d2) | 
                            Q(to_date__isnull=True))

                assocs = projassoc.filter(*args).order_by("-from_date")
                if assocs:
                    if user_rates: 
                        # Two project associations can't overlap
                        if user_rates[len(user_rates)-1][1]==d1:
                            user_rates[len(user_rates)-1][1] = d1 - timedelta(days=1)
                    user_rates.append([d1, d2, assocs[0].client_rate])

            user_rates = join_dups(user_rates)
            rates.append((user, user_rates))

        # Generate hours with rates according to project associations periods
        t_hours = []
        for user, rate_list in rates:
            for rate in rate_list:
                hours = self.objects.filter(date__gte=rate[0],
                                            date__lte=rate[1],
                                            project=project,
                                            user=user)
                hours = hours.values('user__username').annotate(Sum("hours_booked"))
                if hours:
                    hours = hours[0]
                    repeated = filter(lambda d: d['user__username']==user.username and d['rate']==rate[2], 
                                      t_hours)
                    if repeated:
                        i = t_hours.index(repeated[0])
                        t_hours[i]['hours_booked__sum']+=hours['hours_booked__sum']
                    elif hours:
                        hours['rate'] = rate[2]
                        t_hours.append(hours)

        return t_hours


    @classmethod
    def project_tasks_hours_log(self, project, from_date, to_date):
        return self.objects.filter(date__gte=from_date,
                                   date__lte=to_date,
                                   project=project).order_by('date')

    @classmethod
    def hours_per_project_a_day(klass, user, a_date, project=None):
        kwargs = dict(date=a_date,
                      user__username=user.user.username)

        if not (project is None):
            kwargs['project'] = project

        return sum(log.hours_booked
                   for log in klass.objects.filter(**kwargs))

    @classmethod
    def get_log_hours_per_selected_project(klass, user, project_name, from_date, to_date):
        return klass.hours_per_project(user, from_date, to_date, project=project_name)

    # All hours of a CSV project are billable, think Tutos, etc.

    #billable_hours = hours_per_project
    @classmethod
    def billable_hours(klass, user, from_date, to_date, project=None):
        qset = klass._query(user, from_date, to_date, project, billable=True)
        return sum(log.hours_booked for log in qset)

    #billable_hours_a_day = hours_per_project_a_day
    @classmethod
    def billable_hours_a_day(klass, user, a_date, project=None):
        kwargs = dict(date=a_date,
                      user__username=user.user.username,
                      project__billable=True)

        if not (project is None):
            kwargs['project'] = project

        return sum(log.hours_booked
                   for log in klass.objects.filter(**kwargs))


    def _to_tuple(self):
        return (self.project.name, self.task_name, self.description,
                self.hours_booked, self.date, self.user)

    @classmethod
    def report(klass, user, from_date, to_date, project=None):
        if project is not None:
            return (log._to_tuple()
                    for log in klass.objects.filter(date__gte=from_date,
                                                    date__lte=to_date,
                                                    user__username=user.user.username,
                                                    project__name=project))
        else:
            return (log._to_tuple()
                    for log in klass.objects.filter(date__gte=from_date,
                                                    date__lte=to_date,
                                                    user__username=user.user.username))

    @classmethod
    def get_summary_per_project(self, user, from_date, to_date, with_rates=False):
        if with_rates:
            return ((item[0].get_external_source(), item[0].name, True, item[2], item[3])
                    for item in
                    self.hours_grouped_by_project_with_rates(user, from_date, to_date)
                    if item is not None)
        else:
            return ((item[0].get_external_source(), item[0].name, True, item[2])
                    for item in
                    self.hours_grouped_by_project(user, from_date, to_date)
                    if item is not None)

    @classmethod
    def get_client_summary_per_project(self, client, from_date, to_date, with_rates=False):
        projects = client.project_set.all()
        projects_users_hours = {}

        if with_rates:

            # Excluding fixed price projects
            projects = projects.filter(billing_type='HOUR')

            for p in projects:
                project_hours = TimeLog.project_hours_grouped_by_rate(p, from_date, to_date)
                if project_hours:
                    projects_users_hours[p.external_id]=[]

                    projects_users_hours[p.external_id] += [(i['user__username'], 
                                                             i['hours_booked__sum'], 
                                                             i['rate']) 
                                                            for i in project_hours]
        else:
            for p in projects:
                project_hours = TimeLog.project_hours(p, from_date, to_date)
                if project_hours:
                    projects_users_hours[p.external_id]=[]
                    projects_users_hours[p.external_id] += [(i['user__username'], 
                                                             i['hours_booked__sum'])
                                                            for i in project_hours]

        return projects_users_hours

    @classmethod
    def get_client_task_log_summary_per_project(self, client, from_date, to_date):
        projects = client.project_set.all()
        projects_users_hours = {}
        for p in projects:
            project_hours = TimeLog.project_tasks_hours_log(p, from_date, to_date)
            if project_hours:
                projects_users_hours[p.external_id]={}
                for i in project_hours:
                    try:
                        projects_users_hours[p.external_id][i.user.username].append(
                            (i.date, i.description, round(i.hours_booked,2)))
                    except KeyError:
                        projects_users_hours[p.external_id][i.user.username] = [(i.date, i.description, round(i.hours_booked,2))]
        return projects_users_hours

def join_dups(l):
    """ Helper function to join consecutive project associations with same rate """
    if not l:
        return l
    
    i = 0
    for item in l:
        if item[2]==l[i][2]: continue
        i += 1
        l[i] = (l[i][0], item[1], l[i][2])
    l[i] = (l[i][0], item[1], l[i][2])
    del l[i+1:]
    return l
