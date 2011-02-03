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
#from external_source import ExternalSource

class Dump(models.Model):
    date = models.DateField()
    creator = models.CharField(max_length=100)
    source = models.ForeignKey('ExternalSource', null=True)

    class Meta:
        app_label = 'eff'

    def __unicode__(self):
        return u'Dump - source: %s, created by: %s, date: %s' % (self.source,
                                                                 self.creator,
                                                                 self.date)
