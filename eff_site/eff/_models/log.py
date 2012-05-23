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
from django.db.models import Sum

from dump import Dump

from django.db.models import Q
from customfields import HourField
from decimal import Decimal


class TimeLog(models.Model):

    date = models.DateField()
    project = models.ForeignKey(Project)
    task_name = models.CharField(max_length=500, blank=True)
    user = models.ForeignKey(User)
    hours_booked = HourField()
    description = models.TextField(blank=True)

    dump = models.ForeignKey(Dump)

    class Meta:
        app_label = 'eff'

    def __unicode__(self):
        return u'[%s, %s, %s, %s]' % (self.date, self.project, self.user,
            self.hours_booked)

    @classmethod
    def _query(cls, user, from_date, to_date, project=None, billable=False):
        kwargs = dict(date__gte=from_date,
                      date__lte=to_date,
                      # it's an instance of UserProfile
                      user__username=user.user.username)

        if not (project is None):
            kwargs['project'] = project

        if billable:
            kwargs['project__billable'] = True

        return cls.objects.filter(**kwargs)

    @classmethod
    def hours_per_project(cls, user, from_date, to_date, project=None):
        qset = cls._query(user, from_date, to_date, project)
        return sum(log.hours_booked for log in qset)

    @classmethod
    def user_projects(cls, user, from_date, to_date):
        return Project.objects.filter(
                                    timelog__user__username=user.user.username,
                                    timelog__date__gte=from_date,
                                    timelog__date__lte=to_date
                ).distinct()

    @classmethod
    def _group_by_project(cls, qset):
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
    def hours_grouped_by_project(cls, user, from_date, to_date):
        qset = cls._query(user, from_date, to_date, None)
        return cls._group_by_project(qset)

    @classmethod
    def hours_grouped_by_project_with_rates(cls, user, from_date, to_date):
        project_rates = []
        # Get the projects related to this user in this period
        user_projects = cls.user_projects(user, from_date, to_date)

        for project in user_projects:
            rates = {}
            # Get the timelogs in this period
            timelogs = project.timelog_set.filter(
                Q(user__username=user.user.username),
                Q(date__gte=from_date),
                Q(date__lte=to_date)).order_by('date')

            # Discard project associations out of the period
            projassoc = ProjectAssoc.objects.filter(
                Q(member__user__username=user.user.username),
                Q(project=project),
                ~Q(from_date__gt=to_date),
                ~Q(to_date__lt=from_date)).order_by('from_date')

            # Get the rates for each project.
            for period in projassoc.values('from_date', 'to_date',
                                           'user_rate'):
                # All timelogs before this period belong to a previous period
                # or do not belong to any period, so they have rate = 0.
                for t in timelogs:
                    if t.date < period['from_date']:
                        rates[Decimal('0.00')] = rates.get(Decimal('0.00'),
                                                           Decimal('0.00')) +\
                                                           t.hours_booked
                    else:
                        break
                # Discard timelogs already processed
                timelogs = timelogs.exclude(date__lt=period['from_date'])
                # All timelogs inside this period have rate equal to the one
                # set in the projassoc.
                for t in timelogs:
                    if t.date <= period['to_date']:
                        rates[Decimal(period['user_rate'])] = rates.get(
                            Decimal(period['user_rate']), Decimal('0.00')) + \
                            t.hours_booked
                    else:
                        break
                # Discard timelogs already processed
                timelogs = timelogs.exclude(date__lte=period['to_date'])

            # All remaining timelogs have rate = 0
            tl_hours = map(lambda log: log['hours_booked'],
                           timelogs.values('hours_booked'))
            if timelogs:
                rates[Decimal('0.00')] = rates.get(Decimal('0.00'),
                                                   Decimal('0.00')) + \
                                                   sum(tl_hours)

            for rate, hours in rates.items():
                project_rates.append((project, '', hours, rate))

        return project_rates

    @classmethod
    def project_hours(cls, project, from_date, to_date):
        hours = cls.objects.filter(date__gte=from_date,
                                    date__lte=to_date,
                                    project=project)
        hours = hours.values('user__username').annotate(Sum("hours_booked"))
        return hours

    @classmethod
    def project_hours_grouped_by_rate(cls, project, from_date, to_date):
        users_rates = []
        # Get the users related to this project
        project_users = map(lambda member: member.user,
                            project.members.all().distinct())

        for user in project_users:
            rates = {}
            # Get the timelogs in this period
            timelogs = project.timelog_set.filter(
                Q(user=user),
                Q(date__gte=from_date),
                Q(date__lte=to_date)).order_by('date')

            # Discard project associations out of the period
            projassoc = ProjectAssoc.objects.filter(
                Q(member__user=user),
                Q(project=project),
                ~Q(from_date__gt=to_date),
                ~Q(to_date__lt=from_date)).order_by('from_date')

            # Get the rates for each user.
            for period in projassoc.values('from_date', 'to_date',
                                           'client_rate'):
                # All timelogs before this period belong to a previous period
                # or do not belong to any period, so they have rate = 0.
                for t in timelogs:
                    if t.date < period['from_date']:
                        rates[Decimal('0.00')] = rates.get(Decimal('0.00'),
                                                           Decimal('0.00')) +\
                                                           t.hours_booked
                    else:
                        break
                # Discard timelogs already processed
                timelogs = timelogs.exclude(date__lt=period['from_date'])
                # All timelogs inside this period have rate equal to the one set
                # in the projassoc.
                for t in timelogs:
                    if t.date <= period['to_date']:
                        rates[Decimal(period['client_rate'])] = rates.get(
                            Decimal(period['client_rate']), Decimal('0.00')) + \
                            t.hours_booked
                    else:
                        break
                # Discard timelogs already processed
                timelogs = timelogs.exclude(date__lte=period['to_date'])

            # All remaining timelogs have rate = 0
            tl_hours = map(lambda log: log['hours_booked'],
                           timelogs.values('hours_booked'))
            if timelogs:
                rates[Decimal('0.00')] = rates.get(Decimal('0.00'),
                                                   Decimal('0.00')) + \
                                                   sum(tl_hours)

            for rate, hours in rates.items():
                users_rates.append({'user__username': user.username,
                                    'rate': rate, 'hours_booked__sum': hours})

        return users_rates

    @classmethod
    def project_tasks_hours_log(cls, project, from_date, to_date):
        return cls.objects.filter(date__gte=from_date,
                                   date__lte=to_date,
                                   project=project).order_by('date')

    @classmethod
    def hours_per_project_a_day(cls, user, a_date, project=None):
        kwargs = dict(date=a_date,
                      user__username=user.user.username)

        if not (project is None):
            kwargs['project'] = project

        return sum(log.hours_booked
                   for log in cls.objects.filter(**kwargs))

    @classmethod
    def get_log_hours_per_selected_project(cls, user, project_name, from_date,
        to_date):
        return cls.hours_per_project(user, from_date, to_date,
            project=project_name)

    # All hours of a CSV project are billable, think Tutos, etc.

    #billable_hours = hours_per_project
    @classmethod
    def billable_hours(cls, user, from_date, to_date, project=None):
        qset = cls._query(user, from_date, to_date, project, billable=True)
        return sum(log.hours_booked for log in qset)

    #billable_hours_a_day = hours_per_project_a_day
    @classmethod
    def billable_hours_a_day(cls, user, a_date, project=None):
        kwargs = dict(date=a_date,
                      user__username=user.user.username,
                      project__billable=True)

        if not (project is None):
            kwargs['project'] = project

        return sum(log.hours_booked
                   for log in cls.objects.filter(**kwargs))

    def _to_tuple(self):
        return (self.project.name, self.task_name, self.description,
                self.hours_booked, self.date, self.user)

    @classmethod
    def report(cls, user, from_date, to_date, project=None):
        if project is not None:
            return (log._to_tuple()
                    for log in cls.objects.filter(
                        date__gte=from_date,
                        date__lte=to_date,
                        user__username=user.user.username,
                        project__name=project))
        else:
            return (log._to_tuple()
                    for log in cls.objects.filter(
                        date__gte=from_date,
                        date__lte=to_date,
                        user__username=user.user.username))

    @classmethod
    def get_summary_per_project(cls, user, from_date, to_date,
        with_rates=False):
        if with_rates:
            return ((item[0].get_external_source(), item[0].name, True, item[2],
                item[3])
                    for item in
                    cls.hours_grouped_by_project_with_rates(user, from_date,
                        to_date)
                    if item is not None)
        else:
            return ((item[0].get_external_source(), item[0].name, True, item[2])
                    for item in
                    cls.hours_grouped_by_project(user, from_date, to_date)
                    if item is not None)

    @classmethod
    def get_client_summary_per_project(cls, client, from_date, to_date,
        with_rates=False):
        projects = client.project_set.all()
        projects_users_hours = {}

        if with_rates:

            # Excluding fixed price projects
            projects = projects.filter(billing_type='HOUR')

            for p in projects:
                project_hours = TimeLog.project_hours_grouped_by_rate(p,
                    from_date, to_date)
                if project_hours:
                    projects_users_hours[p.external_id] = []

                    projects_users_hours[p.external_id] += [
                        (i['user__username'], i['hours_booked__sum'], i['rate'])
                        for i in project_hours]
        else:
            for p in projects:
                project_hours = TimeLog.project_hours(p, from_date, to_date)
                if project_hours:
                    projects_users_hours[p.external_id] = []
                    projects_users_hours[p.external_id] += [
                        (i['user__username'], i['hours_booked__sum']) \
                        for i in project_hours]

        return projects_users_hours

    @classmethod
    def get_client_task_log_summary_per_project(cls, client, from_date,
        to_date):
        projects = client.project_set.all()
        projects_users_hours = {}

        for p in projects:
            project_hours = TimeLog.project_tasks_hours_log(p, from_date,
                to_date)

            if project_hours:
                projects_users_hours[p.external_id] = {}

                for i in project_hours:
                    name = i.user.username
                    user_data = projects_users_hours[p.external_id]
                    info = (i.date, i.description, i.hours_booked)

                    if name in user_data:
                        user_data[name].append(info)
                    else:
                        user_data[name] = [info]

        return projects_users_hours
