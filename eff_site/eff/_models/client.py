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
from log import TimeLog
from project import Project


class Currency(models.Model):
    # Codes as in http://en.wikipedia.org/wiki/ISO_4217#Active_codes
    ccy_code = models.CharField(max_length=3, primary_key=True)
    ccy_symbol = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        app_label = 'eff'
        verbose_name_plural = 'currencies'
        ordering = ['ccy_code']

    def __unicode__(self):
        return u'%s' % (self.ccy_code,)


class Client(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)

    country = models.CharField(max_length=100)
    billing_email_address = models.EmailField()
    contact_email_address = models.EmailField(blank=True)

    currency = models.ForeignKey(Currency, to_field="ccy_code", default="USD")

    external_source = models.ForeignKey('ExternalSource')
    external_id = models.CharField(max_length=255)

    class Meta:
        app_label = 'eff'
        ordering = ['name']

    def __unicode__(self):
        return u'%s' % (self.name,)

    def save(self, *args, **kwargs):
        if self.slug is None:
            self.slug = slugify(self.name)
        super(Client, self).save(*args, **kwargs)

    def report(self, from_date, to_date, detailed=False, with_rates=False):
        report_by_project = {}
        detailed_hours = {}

        report = TimeLog.get_client_summary_per_project(self, from_date,
                                                        to_date, with_rates)
        if detailed:
            summary = TimeLog.get_client_task_log_summary_per_project(self,
                                                            from_date, to_date)
            detailed_hours.update(summary)
        report_by_project.update(report)

        report_by_project = sorted(report_by_project.items(),
                                   key=lambda x: x[0])

        totalHrs = []
        for p_id, usr_hs in report_by_project:
            totalHrs.append(sum(map(lambda x: x[1], usr_hs)))

        if detailed:
            def format_task_log(a, b, c):
                if not b[0] in a.keys():
                    return []
                if not c[0] in a[b[0]]:
                    return []
                return a[b[0]][c[0]]

            report_by_project = map(lambda x: (x[0], map(lambda y: (y[0], y[1],
                                format_task_log(detailed_hours, x, y)), x[1])),
                                    report_by_project)

        report_by_project = map(lambda (p, ul):
                                (Project.objects.get(external_id=p).name, ul),
                                report_by_project)

        return zip(report_by_project, totalHrs)


class BillingEmail(models.Model):
    SEND_AS_CHOICES = [('to', 'TO'), ('cc', 'CC'), ('bcc', 'BCC')]
    email_address = models.EmailField()
    send_as = models.CharField(default='to', max_length=3,
                               choices=SEND_AS_CHOICES)
    client = models.ForeignKey(Client)

    class Meta:
        app_label = 'eff'
        verbose_name_plural = 'Billing email addresses'
        ordering = ['client', 'email_address']

    def __unicode__(self):
        return u'%s send as %s' % (self.email_address, self.send_as)
