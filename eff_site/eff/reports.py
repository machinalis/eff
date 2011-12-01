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


from datetime import datetime
from django.contrib.auth.models import User
import itertools
from django.contrib.humanize.templatetags import humanize
from decimal import Decimal

# For further usage i.e. to calculate totals
class ClientReverseBilling(dict):
    pass

class UserReverseBilling(dict):
    pass

class FixedPriceClientReverseBilling(dict):
    pass

def format_invoice_period(from_date, to_date):
    invoice_period = from_date.strftime("%B ")
    day = int(from_date.strftime("%d"))
    invoice_period += humanize.ordinal(str(day))
    invoice_period += to_date.strftime(" - %B ")
    day = int(to_date.strftime("%d"))
    invoice_period += humanize.ordinal(str(day))
    invoice_period += from_date.strftime(", %Y")
    return invoice_period

def format_report_data(rep, client, from_date, to_date, detailed=False):
    report_list = []
    total_sum = Decimal('0.00')
    for p, users in rep.iteritems():
        user_list = []
        for user in users:
            du = User.objects.get(username=user[0])
            if not detailed:
                user_d = {'full_name' : du.first_name + " " + du.last_name, 
                          'hs' : "%.2f" % user[1]}
                # Include rates in report
                if len(user)>2:
                    user_total = (Decimal(str(user[1])) * Decimal(str(user[2])))
                    total_sum += user_total
                    user_d.update({'rate' : "%.2f" % user[2],
                                   'total' : "%.2f" % user_total})
                user_list.append(user_d)
            else:
                user_list.append({'full_name' : du.first_name + " " + du.last_name, 'hs': "%.2f" % user[1],
                                  'hs_detail' : map(lambda x: {'date': x[0].strftime("%d/%m/%Y"), 
                                                               'desc': x[1] , 
                                                               'hs': "%.2f" % x[2]}, user[2])})
        report_list.append({'project_name' : p, 'users' : user_list})
    state_and_country = client.state or ''
    if state_and_country.strip(): state_and_country += ' - '
    state_and_country += client.country
    client_data = {'name' : client.name or '',
                   'address' : client.address or '',
                   'city' : client.city or '',
                   'state_and_country' : state_and_country, 
                   'currency' : client.currency.ccy_symbol or client.currency.ccy_code,
                 }
    reverse_billing = ClientReverseBilling(projects_users = report_list,
                                           client_data = client_data,
                                           invoice_period = format_invoice_period(from_date, to_date),
                                           reference = "%s%s%s" % (client.name.lower(), from_date.year, from_date.strftime("%m"), ),
                                           today = datetime.now().strftime("%A, %d %B %Y"),
                                           total = "%.2f" % total_sum)
    return reverse_billing

def format_report_data_user(rep, user, from_date, to_date, detailed=False):
    report_list = map(lambda p: {'project_name' : p[1], 
                                 'user_hs' : isinstance(p[3], float) and ("%.2f" % p[3]) or \
                                     map(lambda r: {'hs' : "%.2f" % r[0], 
                                                    'rate' : "%.2f" % r[1],
                                                    'total' : "%.2f" % (round(r[0], 2)*round(r[1], 2))
                                                    }, 
                                         p[3])
                                 }, 
                      rep)


    sub_total = 0.0
    if isinstance(rep[0][3], list):
        sub_total = "%.2f" % sum(map(lambda c: round(float(c['total']), 2), 
                                     itertools.chain(*map(lambda d: d['user_hs'], report_list))))
    
    state_and_country = user.get_profile().state.strip() or ''
    if state_and_country and user.get_profile().country.strip(): 
        state_and_country += ' - ' + user.get_profile().country
    else:
        state_and_country += user.get_profile().country or ''
    user_data = {'full_name' : user.get_full_name() or '',
                 'address' : user.get_profile().address or '',
                 'city' : user.get_profile().city or '',
                 'state_and_country' : state_and_country,
                 }

    if detailed:
        hs_detail = {'hs_detail' : map(lambda x: {'date': x[4].strftime("%d/%m/%Y"), 
                                                  'desc': x[2], 
                                                  'hs': "%.2f" % x[3],
                                                  'project' : x[0],
                                                  'task' : x[1]}, rep)}
        user_data.update(hs_detail)
        totalHrs = 0
        for r in rep:
            totalHrs += r[3]

        user_data.update({'total_hs' : totalHrs})

    reverse_billing = UserReverseBilling(user_hours = report_list,
                                         sub_total = sub_total,
                                         user_data = user_data,
                                         invoice_period = format_invoice_period(from_date, to_date),
                                         reference = "%s_%s%s%s" % (user.first_name.lower(), 
                                                                    user.last_name.lower(), 
                                                                    from_date.year, 
                                                                    from_date.strftime("%m"), ),
                                         today = datetime.now().strftime("%A, %d %B %Y"))
    return reverse_billing
