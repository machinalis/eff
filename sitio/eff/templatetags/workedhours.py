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

import time
from datetime import date

from django import template
from sitio.eff._models.user_profile import UserProfile
#from sitio.settings import DATE_FORMAT

register = template.Library()

def aux_mk_time(date_string):
    _date = time.mktime(time.strptime(date_string, '%Y-%m-%d'))
    _date = date.fromtimestamp(_date)
    return _date

@register.filter(name='totalhours')
def totalhours(profile, date_string):
    dates = date_string.split()
    try:
        return profile.num_loggable_hours(aux_mk_time(dates[0]), aux_mk_time(dates[1]))
    except:
        raise
        pass # filters should fail silently

@register.filter(name='workedhours')
def workedhours(profile, date_string):
    dates = date_string.split()
    try:
        return profile.get_worked_hours(aux_mk_time(dates[0]), aux_mk_time(dates[1]))
    except:
        raise
        pass # filters should fail silently

@register.filter(name='percentage')
def percentage(profile, date_string):
    dates = date_string.split()
    try:
        return profile.percentage_hours_worked(aux_mk_time(dates[0]), aux_mk_time(dates[1]))
    except:
        raise
        pass # filters should fail silently

@register.filter(name='odd')
def odd(num):
    try:
        return int(num) % 2
    except:
        raise
        pass # filters should fail silently
