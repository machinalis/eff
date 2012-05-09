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
from customfields import MoneyField


class ProjectAssoc(models.Model):
    project = models.ForeignKey('Project')
    member = models.ForeignKey('UserProfile')
    client_rate = MoneyField()
    user_rate = MoneyField()
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
    fixed_price = MoneyField(blank=True, null=True)

    class Meta:
        app_label = 'eff'

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.client.name)

    def get_external_source(self):
        return self.client.external_source

