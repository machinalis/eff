# Copyright 2011 Machinalis: http://www.machinalis.com/
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
from user_profile import UserProfile


class ExternalId(models.Model):
    login = models.CharField(max_length=100)
    source = models.ForeignKey('ExternalSource', null=True)
    userprofile = models.ForeignKey(UserProfile)

    class Meta:
        app_label = 'eff'

    def __unicode__(self):
        return u'%s' % (self.login,)

class ExternalSource(models.Model):
    name = models.CharField(max_length=200)
    fetch_url = models.CharField(max_length=500, blank=True)
    username = models.CharField(max_length=50, blank=True)
    password = models.CharField(max_length=50, blank=True)
    csv_directory = models.CharField(max_length=100, blank=True)
    csv_filename = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        app_label = 'eff'

    def __unicode__(self):
        return u'%s' % (self.name,)
