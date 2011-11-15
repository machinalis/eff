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

import os
import os.path
import time
import string
import tempfile
import csv
import urlparse
import operator

from urllib import quote, urlencode
from subprocess import Popen
from datetime import date, timedelta, datetime

from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template import RequestContext, loader, Context
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils import simplejson
from django.contrib.auth.models import User
from django.conf import settings
from django import forms

from dateutil.relativedelta import relativedelta

from relatorio.templates.opendocument import Template
from reports import format_report_data, format_invoice_period
from reports import format_report_data_user, FixedPriceClientReverseBilling

from eff.models import AvgHours, Wage, TimeLog, Project, Client, UserProfile
from eff.models import ExternalId, ExternalSource, Dump

from eff.utils import overtime_period, previous_week, week, month, period
from eff.utils import Data, DataTotal, debug, ERROR, load_dump, _date_fmts
from eff.utils import validate_header

from eff.forms import AvgHoursForm, EffQueryForm, UserProfileForm
from eff.forms import UsersChangeProfileForm, UserPassChangeForm
from eff.forms import UserAddForm, ClientReportForm, DumpUploadForm

cur_dir = os.path.dirname(os.path.abspath(__file__))

# ==================== internals ====================

OVERTIME_FLAG = 'overtime_nav'
MONTHLY_FLAG = 'monthly_nav'

def __get_context(request):
    context =  RequestContext(request)
    context['hostname'] = request.get_host()
    context['title'] = "Efficiency"
    return context

def __aux_mk_time(date_string):
    _date = time.mktime(time.strptime(date_string, settings.DATE_FORMAT))
    _date = date.fromtimestamp(_date)
    return _date

default_date = __aux_mk_time(date.today().strftime(settings.DATE_FORMAT))
def __process_dates(request):
    context = __get_context(request)
    if request.method == 'GET':
        try:
            from_date = __aux_mk_time(request.GET['from_date'])
            to_date = __aux_mk_time(request.GET['to_date'])
        except (KeyError, ValueError):
            context['errors'] = ["Fecha invalida"]
            context['from_date'] = default_date
            context['to_date'] = default_date
        else:
            context['from_date'] = from_date
            context['to_date'] = to_date

    assert('from_date' in context and 'to_date' in context)
    return context

def __process_period(request, is_prev):
    context = __process_dates(request)
    from_date = context['from_date']
    to_date = context['to_date']

    if is_prev:
        reference_date = context['from_date'] - relativedelta(days=1)
        op = operator.sub
    else:
        reference_date = context['to_date'] + relativedelta(days=1)
        op = operator.add

    aux = None
    if OVERTIME_FLAG in request.GET:
        (from_date, to_date) = overtime_period(reference_date)
        aux = OVERTIME_FLAG
    elif MONTHLY_FLAG in request.GET:
        (from_date, to_date) = month(reference_date)
        aux = MONTHLY_FLAG
    else:
        (from_date, to_date) = period(context['from_date'],
                                      context['to_date'],
                                      op)

    # grab the path from the referer
    parsed_result = urlparse.urlparse(request.META['HTTP_REFERER'])
    path = parsed_result.path
    parsed_query = urlparse.parse_qs(parsed_result.query)

    # add other options, if available
    if aux:
        parsed_query[aux] = True

    # the format of the date arguments in the query depends on the referer
    if path != '/efi/charts/':
        # change the date in the query
        parsed_query['from_date'] = from_date
        parsed_query['to_date'] = to_date

        qstring = urlencode(parsed_query, True)
        redirect_to = '%s?%s' % (path, qstring)
    else:
        # change the dates from the query
        parsed_query['dates'] = '%s,%s' % (from_date, to_date)
        qstring = urlencode(parsed_query, True)
        redirect_to = '%s?%s' % (path, qstring)

    return HttpResponseRedirect(redirect_to)

def __encFloat(lof, maxval):
    simpleEncoding =  string.uppercase + string.lowercase + string.digits
    return "".join([simpleEncoding[min(int(round(i*61/maxval,1)), 61)] for i in lof])

def __encList(llof, maxval):
    return ",".join([__encFloat(i, maxval) for i in llof])

def __enough_perms(u):
    return (u.has_perm('eff.view_billable') and u.has_perm('eff.view_wage'))

def chart_values(username_list, from_date, to_date, request_user):
    values = {}
    monthdict = {1:'Ene', 2:'Feb', 3:'Mar', 4:'Abr', 5:'May', 6:'Jun',
                 7:'Jul', 8:'Ago', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dic'}

    maxdays = 42
    delta = timedelta(days=1)

    user_list = User.objects.filter(username__in=username_list)
    profile_list = [user.get_profile() for user in user_list]

    maxhours = len(username_list) * 24
    if len(username_list) <= 3 :
        cantidad = 2
    elif len(username_list) <= 6:
        cantidad = 4
    elif len(username_list) <= 12:
        cantidad = 8
    else:
        cantidad = 16

    if len(username_list) < 2:
        values['height'] = 240
    else:
        values['height'] = 400

    maxhours_labels = range(0, maxhours, cantidad)
    maxhours_labels.append(maxhours)
    hours_labels = "".join([s for s in ["%d|"% l for l in maxhours_labels]])
    labels = "1:|" + hours_labels + "0:|"
    nombres = "".join(u.first_name + ", " for u in user_list)
    values['name'] = nombres.strip(", ")
    worked_hours_list = []
    billable_hours = []
    current_month = from_date.month
    months = ':|' + monthdict[current_month] + '|'
    tmp_date = from_date

    while tmp_date <= to_date:
        wh = 0
        for profile in profile_list:
            wh += profile.get_worked_hours_per_day(tmp_date)
        worked_hours_list.append(wh)
        if __enough_perms(request_user):
            bh = 0
            for profile in profile_list:
                bh += profile.billable_hours_a_day(tmp_date)
            billable_hours.append(bh)
        else:
            billable_hours.append(0)
        labels += tmp_date.strftime("%d")+"|"
        tmp_date += delta
        if current_month != tmp_date.month:
            current_month = tmp_date.month
            months += monthdict[current_month] + '|'
    values['chart_values'] = __encList([billable_hours,
                                       [a-b for (a,b) in zip(worked_hours_list, billable_hours)]], maxhours)

    values['chart_type'] = 'bvs'
    if (to_date - from_date) <= timedelta(days=maxdays):
        values['width'] = (to_date - from_date).days * 24 + 50
        values['chart_labels'] = labels + '2' + months.strip('|')
        values['chart_axis'] = 'x,y,x'
        values['bar_format'] = '18,2'
    else:
        values['width'] = 640
        values['bar_format'] = '2,1'
        values['chart_axis'] = 'y,x'
        values['chart_labels'] = "0:|"+ hours_labels + '1' + months.strip('|')
        idx = "1,0,"
        last_month = from_date.month
        tmp_date = from_date

        while tmp_date <= to_date:
            tmp_date += delta
            if last_month != tmp_date.month:
                idx += "%d," % (tmp_date - from_date).days
                last_month = tmp_date.month
        values['axis_range'] = 'chxp=' + idx.strip(',')
        #values['extra'] = 'chm=D,FF89F9,1,0,3,1'

    if __enough_perms(request_user):
        values['chco'] = '4d89f9,c6d9fd'
    else:
        values['chco'] = '4d89f9'

    return values

# ==================== Views ====================

def index(request):
    context = __get_context(request)
    return render_to_response('base.html', context)

@login_required
@user_passes_test(__enough_perms, login_url='/accounts/login/')
def update_hours(request, username):

    context = __get_context(request)
    user = User.objects.get(username=username)
    profile = user.get_profile()

    context['errors'] = []

    data = {}

    data['address'] = profile.address
    data['phone_number'] = profile.phone_number

    data['first_name'] = profile.user.first_name
    data['last_name'] = profile.user.last_name

    data['personal_email'] = profile.personal_email
    data['city'] = profile.city
    data['state'] = profile.state
    data['country'] = profile.country

    context['profile_form'] = UserProfileForm(data)

    #######################################
    # Auxiliary functions which generate forms

    def navghours_form_generator (size):
        d = dict()
        for i in xrange(size):
            d['ah_date%d' % i] = forms.DateField(required=False, label='Fecha:')
            d['amount_of_hours%d' % i] = forms.FloatField(required=False,
                                                            label='Cantidad de horas por día:')
        return type('NAvgHoursForm', (forms.Form,), d)

    def nwage_form_generator (size):
        d = dict()
        for i in xrange(size):
            d['w_date%d' % i] = forms.DateField(required=False, label='Fecha:')
            d['amount%d' % i] = forms.FloatField(required=False, label='Monto por hora:')
        return type('NWageForm', (forms.Form,), d)

    #######################################
    # Create form and fill it with data

    def initialize_form (queryset, context, generator,
                         form_name, arg_name_1, arg_name_2,
                         attr_name_1, attr_name_2):
        length = queryset.count()
        form_class = generator(length+1)

        data = dict()
        for i in xrange(length):
            data[(arg_name_1+'%d') % i] = getattr(qs[i], attr_name_1)
            data[(arg_name_2+'%d') % i] = getattr(qs[i], attr_name_2)

        context[form_name] = form_class(data)
        context[form_name+'_size'] = length + 1
        return form_class

    # Constructs form for introducing data on hours worked per day.
    qs = user.avghours_set.all()
    NAvgHoursForm = initialize_form(qs, context, navghours_form_generator,
                                    'avghours_form', 'ah_date', 'amount_of_hours',
                                    'date', 'hours')

    # Constructs form for introducing "wage" data.
    qs = user.wage_set.all()
    NWageForm = initialize_form(qs, context, nwage_form_generator,
                                'wage_form', 'w_date', 'amount',
                                'date', 'amount_per_hour')

    if request.method == 'POST':
        post = request.POST.copy()

        profile_form = UserProfileForm(post)

        if profile_form.is_valid():

            profile.address = profile_form.cleaned_data['address']
            if profile_form.cleaned_data['phone_number'] != None:
                profile.phone_number =\
                    str(profile_form.cleaned_data['phone_number'])
            else:
                profile.phone_number = ''

            profile.personal_email = profile_form.cleaned_data['personal_email']
            profile.city = profile_form.cleaned_data['city']
            profile.state = profile_form.cleaned_data['state']
            profile.country = profile_form.cleaned_data['country']

            profile.save()

            profile.user.first_name = profile_form.cleaned_data['first_name']
            profile.user.last_name = profile_form.cleaned_data['last_name']
            profile.user.save()

            context['profile_form'] = profile_form
        else:
            context['errors'].append('Invalid Profile Form')

        wage_form = NWageForm(post)
        if wage_form.is_valid():
            size = context['wage_form_size']

            user.wage_set.all().delete()

            for i in range(0,size):
                if wage_form.cleaned_data['w_date%d' % i] != None and\
                    wage_form.cleaned_data['amount%d' % i] != None:
                    try:
                        w = Wage(user=user,
                                 date=wage_form.cleaned_data['w_date%d' % i],
                                 amount_per_hour=wage_form.cleaned_data['amount%d' % i])
                        w.save()
                        context['notices'] = ['Update sucessful!']

                    except ValueError, e:
                        context['errors'].append("Error guardando datos de remuneración: %s." % e)
        else:
            context['errors'].append('Invalid Wage Form')

        avghours_form = NAvgHoursForm(post)
        if avghours_form.is_valid():
            size = context['avghours_form_size']

            user.avghours_set.all().delete()

            # there are at most "size" number of filled fields
            for i in range(0,size):
                if avghours_form.cleaned_data['ah_date%d' % i] != None and\
                    avghours_form.cleaned_data['amount_of_hours%d' % i] != None:

                    new_date = avghours_form.cleaned_data['ah_date%d' % i]
                    amount_of_hours = avghours_form.cleaned_data['amount_of_hours%d' % i]
                    try:
                        user.get_profile().add_avg_hours(new_date,
                                                         amount_of_hours)
                    except ValueError, e:
                        context['errors'].append("Error guardando datos"
                                                 " de horario.")
        else:
            context['errors'].append('Invalid Avg Hours Form')

    else: # request.method != 'POST'
        pass

    # Recontrusct the form with new data
    #
    profile = user.get_profile()
    data = dict()

    data['address'] = profile.address
    data['phone_number'] = profile.phone_number

    data['first_name'] = profile.user.first_name
    data['last_name'] = profile.user.last_name
    data['personal_email'] = profile.personal_email
    data['city'] = profile.city
    data['state'] = profile.state
    data['country'] = profile.country

    context['profile_form'] = UserProfileForm(data)
    # Constructs form for introducing data on hours worked per day.
    qs = user.avghours_set.all()
    NAvgHoursForm = initialize_form(qs, context, navghours_form_generator,
                                    'avghours_form', 'ah_date', 'amount_of_hours',
                                    'date', 'hours')
    # Constructs form for introducing "wage" data.
    qs = user.wage_set.all()
    NWageForm = initialize_form(qs, context, nwage_form_generator,
                                'wage_form', 'w_date', 'amount',
                                'date', 'amount_per_hour')

    return render_to_response('update_hours.html', context)

## end update_hours view function #############################################

def eff_check_perms(request, username):
    """
    Check user permission and redirects accordingly
    """
    context = __get_context(request)
    _user = User.objects.get(username=username)

    if not (request.user.is_authenticated() and __enough_perms(request.user)):
        return HttpResponseRedirect(_user.get_profile().get_absolute_url())
    else:
        return HttpResponseRedirect('/updatehours/%s/' % _user.username)

@login_required
def eff_previous_week(request):
    return HttpResponseRedirect('/efi/?from_date=%s&to_date=%s' % previous_week(date.today()))

@login_required
def eff_current_week(request):
    return HttpResponseRedirect('/efi/?from_date=%s&to_date=%s' % week(date.today()))

@login_required
def eff_current_month(request):
    from_date, to_date = month(date.today())
    return HttpResponseRedirect('/efi/?from_date=%s&to_date=%s&%s=True' % (from_date, to_date, MONTHLY_FLAG))

@login_required
def eff_last_month(request):
    from_date, to_date = month(month(date.today())[0]-timedelta(days=1))
    return HttpResponseRedirect('/efi/?from_date=%s&to_date=%s&%s=True' % (from_date, to_date, MONTHLY_FLAG))

@login_required
def eff_horas_extras(request):
    from_date, to_date = overtime_period(date.today())
    return HttpResponseRedirect('/efi/?from_date=%s&to_date=%s&%s=True' % (from_date, to_date, OVERTIME_FLAG))

@login_required
def eff_next(request):
    return __process_period(request, is_prev=False)

@login_required
def eff_prev(request):
    return __process_period(request, is_prev=True)

@login_required
def eff(request):
    """
    When no parameters are provided this view will go directly to the current
    week.
    """
    context = __get_context(request)
    eff_query_form = EffQueryForm()
    context['form'] = eff_query_form

    if request.method == 'GET':
        get_data = request.GET.copy()
        eff_query_form = EffQueryForm(get_data)
        context['form'] = eff_query_form

        if eff_query_form.is_valid():
            from_date = eff_query_form.cleaned_data['from_date']
            to_date = eff_query_form.cleaned_data['to_date']
        else:
            # If form is invalid set dates to the current week and
            # reset the form to the same date
            from_date, to_date = week(date.today())
            context['form'] = EffQueryForm({'from_date': from_date,
                                            'to_date': to_date})

        if not request.user.is_superuser:
            #Less elegant yet nicer in the db, I presume
            object_list = UserProfile.objects.filter(user=request.user)
        else:
            object_list = UserProfile.objects.all()

        data_list = [Data(o,from_date,to_date) for o in object_list]

        wh, lh, bh = 0, 0, 0
        for d in data_list:
            wh += d.worked_hours
            lh += d.loggable_hours
            bh += d.billable_hours
        context['total'] = DataTotal(wh,lh,bh)
        context['object_list'] = data_list
        context['from_date'] = from_date
        context['to_date'] = to_date

        for flag in (OVERTIME_FLAG, MONTHLY_FLAG):
            if flag in request.GET:
                context[flag] = request.GET[flag]

        context['navs'] = [('prev', 'previo', '«'), ('next', 'siguiente', '»')]
        if from_date == to_date:
            aux = "el %s" % from_date
        elif MONTHLY_FLAG in context:
            aux = "durante el mes de %s" % from_date.strftime('%B de %Y') # month name
        elif OVERTIME_FLAG in context:
            aux = "durante el período de horas extras [%s, %s]" % (from_date, to_date)
        else:
            aux = "entre %s y %s" % (from_date, to_date)
        context['title'] = "Horas Logueadas %s" % aux

    return render_to_response('eff_query.html', context)

@login_required
def eff_chart(request, username):

    if not (request.user.has_perm('eff.view_billable') and request.user.has_perm('eff.view_wage')) and \
            request.user.username != username:
        return HttpResponseRedirect('/accounts/login/?next=%s' % quote(request.get_full_path()))

    context = __process_dates(request)
    values = chart_values([username], context['from_date'], context['to_date'], request.user)
    context['users_graph_values'] = [values]

    for flag in (OVERTIME_FLAG, MONTHLY_FLAG):
        if flag in request.GET:
            context[flag] = request.GET[flag]

    context['navs'] = [('prev', 'previo', '«'), ('next', 'siguiente', '»')]

    return render_to_response('profiles/eff_charts.html', context)

@login_required
@user_passes_test(__enough_perms, login_url='/accounts/login/')
def eff_charts(request):

    context = __get_context(request)

    if request.method == 'GET':
        get_data = request.GET.copy()

        if get_data.has_key('monthly_nav'): del get_data['monthly_nav']
        if get_data.has_key('overtime_nav'): del get_data['overtime_nav']

        # Find out what graph has been requested and clean the dictionary accordingly
        if get_data.has_key('MultGraph'):
            # Multiple graphs
            get_data.pop('MultGraph')
            get_data.pop('MultGraph.x')
            get_data.pop('MultGraph.y')
            get_type = 'multi'
        elif get_data.has_key('SumGraph'):
            # Totalization Graphs
            get_data.pop('SumGraph')
            get_data.pop('SumGraph.x')
            get_data.pop('SumGraph.y')
            get_type = 'sum'
        else:
            # Error
            context['errors'] = ["GET: Request de gráfico desconocido"]

        values = []
        users = []
        str_date = get_data['dates']
        dates = str_date.split(',')
        get_data.pop('dates')
        for k in get_data.keys():
            users.append(k)
        try:
            from_date = __aux_mk_time(dates[0])
            to_date = __aux_mk_time(dates[1])
        except (KeyError, ValueError):
            context['errors'] = ["Fecha invalida"]
        else:
            context['from_date'] = from_date
            context['to_date'] = to_date
            if get_type == 'multi':
                values = [chart_values([u], context['from_date'], context['to_date'], request.user) for u in users]
            else:
                if len(users) != 0:
                    values.append(chart_values(users, from_date, to_date, request.user))

    if values == []: context['notices'] = ['No user/s selected.']
    context['users_graph_values'] = values

    for flag in (OVERTIME_FLAG, MONTHLY_FLAG):
        if flag in request.GET:
            context[flag] = request.GET[flag]

    context['navs'] = [('prev', 'previo', '«'), ('next', 'siguiente', '»')]

    return render_to_response('profiles/eff_charts.html', context)

@login_required
def eff_report(request, user_name):

    context = __process_dates(request)
    context['export_allowed'] = True
    if not (request.user.has_perm('eff.view_billable') and request.user.has_perm('eff.view_wage')):
        if request.user.username != user_name:
            return HttpResponseRedirect('/accounts/login/?next=%s' % quote(request.get_full_path()))
        else:
            if 'export' in request.GET:
                return HttpResponseRedirect('/accounts/login/?next=%s' % quote(request.get_full_path()))
            else:
                del context['export_allowed']

    from_date = context['from_date']
    to_date = context['to_date']
    user = User.objects.get(username=user_name)

    project = None
    if 'project' in request.GET:
        project = request.GET['project']
        context['project'] = project

    # detailed log report
    context['report'] = user.get_profile().report(from_date, to_date, project)

    if 'export' in request.GET:
        if request.GET['export'] == 'odt':
            if 'detailed' in request.GET:
                basic = Template(source=None, filepath=os.path.join(cur_dir, '../templates/reporte_usuario_detallado.odt'))
                report_data = format_report_data_user(context['report'], user, from_date, to_date, True)
                basic_generated = basic.generate(o=report_data).render()
                resp = HttpResponse(basic_generated.getvalue(), mimetype='application/vnd.oasis.opendocument.text')
                cd = 'filename=reverse_billing-%s-%s-logs.odt' % (from_date.year, from_date.strftime("%m"), )
                resp['Content-Disposition'] = cd
                return resp
            else:
                basic = Template(source=None, filepath=os.path.join(cur_dir, '../templates/reporte_usuario.odt'))
                report_by_project = list(TimeLog.get_summary_per_project(user.get_profile(), from_date, to_date, True))
                report_by_project.sort(cmp=lambda (x0,x1,x2,x3,x4), (y0,y1,y2,y3,y4) : cmp(x1,y1))
                rep_by_proj = []
                for p in set(map(lambda ph: ph[1], report_by_project)):
                    r4proj = filter(lambda ph: ph[1]==p, report_by_project)
                    rates = sorted(map(lambda ph: (ph[3], ph[4]), r4proj), reverse=True)
                    rep_by_proj.append((r4proj[0][0], r4proj[0][1], r4proj[0][2], rates))

                report_data = format_report_data_user(rep_by_proj, user, from_date, to_date)
                basic_generated = basic.generate(o=report_data).render()
                resp = HttpResponse(basic_generated.getvalue(), mimetype='application/vnd.oasis.opendocument.text')
                cd = 'filename=reverse_billing-%s-%s.odt' % (from_date.year, from_date.strftime("%m"), )
                resp['Content-Disposition'] = cd
                return resp
        elif request.GET['export'] == 'csv':
            response = HttpResponse(mimetype='text/csv')
            if 'detailed' in request.GET:
                cd = 'attachment; filename=reverse_billing_%s_%s_%s_logs.csv' % (user_name, from_date, to_date, )
                response['Content-Disposition'] = cd
                report_data = format_report_data_user(context['report'], user, from_date, to_date, True)
                t = loader.get_template('csv/reporte_usuario_detallado.txt')
                c = Context({'data': report_data['user_data']['hs_detail'],})
            else:
                cd = 'attachment; filename=reverse_billing_%s_%s_%s.csv' % (user_name, from_date, to_date, )
                response['Content-Disposition'] = cd
                report_by_project = list(TimeLog.get_summary_per_project(user.get_profile(), from_date, to_date))
                report_by_project.sort(cmp=lambda (x0,x1,x2,x3), (y0,y1,y2,y3) : cmp(x3,y3))
                report_data = format_report_data_user(report_by_project, user, from_date, to_date)
                t = loader.get_template('csv/reporte_usuario.txt')
                c = Context({'data': report_data['user_hours'],})

            response.write(t.render(c))
            return response

    # report grouped by project
    report_by_project = list(TimeLog.get_summary_per_project(user.get_profile(), from_date, to_date))
    report_by_project.sort(cmp=lambda (x0,x1,x2,x3), (y0,y1,y2,y3) : cmp(x3,y3))

    context['username'] = user_name
    context['target_user'] = user

    # per-project report
    context['report_by_project'] = report_by_project
    context['projects'] = sorted(map(lambda p: p[1], report_by_project))

    # detailed total of hours between [from_date, to_date]
    totalHrs = 0
    for r in context['report']:
        totalHrs += r[3]
    context['TotalHrsDetailed'] = totalHrs
    # total of hours between [from_date, to_date]
    totalHrs = 0
    for r in context['report_by_project']:
        totalHrs += r[3]
    context['TotalHrs'] = totalHrs

    for flag in (OVERTIME_FLAG, MONTHLY_FLAG):
        if flag in request.GET:
            context[flag] = request.GET[flag]

    context['navs'] = [('prev', 'previo', '«'), ('next', 'siguiente', '»')]

    return render_to_response('reporte.html', context)

@login_required
@user_passes_test(__enough_perms, login_url='/accounts/login/')
def eff_update_db(request):

    if not os.path.exists(settings.FLAG_FILE):
        fd = open(settings.FLAG_FILE, 'w')
        fd.write('%s' % date.today().strftime(settings.DATE_FORMAT + ' %H:%M'))
        fd.close()

        # We use a cron job to run the code below now
        # args = (settings.PYTHON_BINARY, settings.FETCH_EXTERNALS_PATH)
        # process = Popen(args, stdout=open(settings.DEBUG_FILE, 'w'),
        #                 close_fds=True)

        response_data = dict(status='ok')
        return HttpResponse(simplejson.dumps(response_data),
                            mimetype='application/json')
    else:
        fd = open(settings.FLAG_FILE, 'r')
        time = fd.readline()
        fd.close()
        response_data = dict(status='wait', last_update=('%s' % time))
        return HttpResponse(simplejson.dumps(response_data),
                            mimetype='application/json')

@login_required
@user_passes_test(__enough_perms, login_url='/accounts/login/')
def eff_administration(request):

    context = {}
    form = UserPassChangeForm()

    if not request.user.is_superuser:
        form.fields['user'].queryset=User.objects.filter(is_superuser=False)

    if request.method == 'POST':
        form = UserPassChangeForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['password']!='':
                user = form.cleaned_data['user']
                user.set_password(form.cleaned_data['password'])
                user.save()
                context['notices'] = ['Update sucessful!']
        else:
            context['errors'] = ['Invalid Form']

    context['form'] = form
    context['title'] = 'Users Change Password'
    return render_to_response('administration.html', context, context_instance=RequestContext(request))

@login_required
@user_passes_test(__enough_perms, login_url='/accounts/login/')
def eff_client_report(request, client_slug):

    client = get_object_or_404(Client, slug=client_slug)
    context = __process_dates(request)
    from_date = context['from_date']
    to_date = context['to_date']

    if 'export' in request.GET:
        if request.GET['export'] == 'odt':
            if 'detailed' in request.GET:
                basic = Template(source=None, filepath=os.path.join(cur_dir, '../templates/reporte_cliente_detallado.odt'))
                report_by_project = dict(map(lambda x:x[0], client.report(from_date, to_date, True)))
                report_data = format_report_data(report_by_project, client, from_date, to_date, True)
                report_data['clientname'] = client.name
                basic_generated = basic.generate(o=report_data).render()
                resp = HttpResponse(basic_generated.getvalue(), mimetype='application/vnd.oasis.opendocument.text')
                cd = 'filename=billing-%s-%s-logs.odt' % (from_date.year, from_date.strftime("%m"), )
                resp['Content-Disposition'] = cd
                return resp
            else:
                basic = Template(source=None, filepath=os.path.join(cur_dir, '../templates/reporte_cliente.odt'))
                report_by_project = dict(map(lambda x:x[0], client.report(from_date, to_date, with_rates=True)))
                report_data = format_report_data(report_by_project, client, from_date, to_date)
                basic_generated = basic.generate(o=report_data).render()
                resp = HttpResponse(basic_generated.getvalue(), mimetype='application/vnd.oasis.opendocument.text')
                cd = 'filename=billing-%s-%s.odt' % (from_date.year, from_date.strftime("%m"), )
                resp['Content-Disposition'] = cd
                return resp
        elif request.GET['export'] == 'csv':
            response = HttpResponse(mimetype='text/csv')
            if 'detailed' in request.GET:
                cd = 'attachment; filename=billing_%s_%s_%s_logs.csv' % (client_slug, from_date, to_date, )
                response['Content-Disposition'] = cd
                report_by_project = dict(map(lambda x:x[0], client.report(from_date, to_date, True)))
                report_data = format_report_data(report_by_project, client, from_date, to_date, True)
                t = loader.get_template('csv/reporte_cliente_detallado.txt')
                c = Context({'data': report_data['projects_users'],})
            else:
                cd = 'attachment; filename=billing_%s_%s_%s.csv' % (client_slug, from_date, to_date, )
                response['Content-Disposition'] = cd
                report_by_project = dict(map(lambda x:x[0], client.report(from_date, to_date)))
                report_data = format_report_data(report_by_project, client, from_date, to_date)
                t = loader.get_template('csv/reporte_cliente.txt')
                c = Context({'data': report_data['projects_users'],})

            response.write(t.render(c))
            return response

    context['report_by_project'] = client.report(from_date, to_date, True)
    context['clientname'] = client.name

    if MONTHLY_FLAG in request.GET:
        context[MONTHLY_FLAG] = request.GET[MONTHLY_FLAG]

    context['navs'] = [('prev', 'previo', '«'), ('next', 'siguiente', '»')]

    return render_to_response('reporte_cliente.html', context)


@login_required
@user_passes_test(__enough_perms, login_url='/accounts/login/')
def eff_client_reports_admin(request):
    context = __get_context(request)

    if 'period' in request.GET:
        if request.GET['period']=='current_month':
            from_date, to_date = month(date.today())
        elif request.GET['period']=='last_month':
            from_date, to_date = month(month(date.today())[0]-timedelta(days=1))
    else:
        if 'from_date' in request.GET and 'to_date' in request.GET:
            from_date = __aux_mk_time(request.GET['from_date'])
            to_date = __aux_mk_time(request.GET['to_date'])
        else:
            # Current week by default
            from_date, to_date = week(date.today())

    initial = {'from_date' : from_date.strftime("%Y-%m-%d"),
               'to_date' : to_date.strftime("%Y-%m-%d")}

    context['title'] = "Reporte de Clientes"

    client_report_form = ClientReportForm(initial=initial)
    context['form'] = client_report_form
    if request.method == 'POST':
        client_report_form = ClientReportForm(request.POST)
        context['form'] = client_report_form
        if client_report_form.is_valid():
            from_date = client_report_form.cleaned_data['from_date']
            to_date = client_report_form.cleaned_data['to_date']
            client = client_report_form.cleaned_data['client']

            redirect_to = '/efi/reporte_cliente/%s/?from_date=%s&to_date=%s' % (client.slug, from_date, to_date,)

            if MONTHLY_FLAG in request.GET:
                redirect_to += '&%s=%s' % (MONTHLY_FLAG, request.GET[MONTHLY_FLAG], )

            return HttpResponseRedirect(redirect_to)

    return render_to_response('admin_reportes_cliente.html', context)

@login_required
@user_passes_test(__enough_perms, login_url='/accounts/login/')
def eff_admin_add_user(request):
    context = {}
    initial = {}
    if 'user' in request.GET:
        initial['username'] = request.GET['user']

    form = UserAddForm(initial=initial)

    if request.method == 'POST':
        form = UserAddForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['password']!='':
                user = User(username=form.cleaned_data['username'])
                user.set_password(form.cleaned_data['password'])
                user.save()

                context['notices'] = ['Update sucessful!']
        else:
            context['errors'] = ['Invalid Form']

    context['form'] = form
    context['title'] = 'Add User'
    return render_to_response('administration.html', context, context_instance=RequestContext(request))

@login_required
@user_passes_test(__enough_perms, login_url='/accounts/login/')
def eff_admin_change_profile(request):
    form = UsersChangeProfileForm()
    context = {}

    if 'user_id' in request.GET:
        user = get_object_or_404(User, id=request.GET['user_id'])
        user_profile = get_object_or_404(UserProfile, user=user)
        form = UsersChangeProfileForm(instance=user_profile)

        if request.method == 'POST':
            form = UsersChangeProfileForm(request.POST, instance=user_profile)
            if form.is_valid():
                form.save()
                context['notices'] = ['Update sucessful!']
            else:
                context['errors'] = ['Invalid Form']

    context['form'] = form
    context['title'] = 'Edit Users Profile'
    return render_to_response('admin_change_users_profile.html', context, context_instance=RequestContext(request))

@login_required
@user_passes_test(__enough_perms, login_url='/accounts/login/')
def profile_detail(request, username):
    user = get_object_or_404(User, username=username)
    p = get_object_or_404(UserProfile, user=user)
    return render_to_response('profiles/profile_detail.html', {'profile': p})

@login_required
@user_passes_test(__enough_perms, login_url='/accounts/login/')
def eff_dump_csv_upload(request):
    """ Allows to import the logs contained in an Eff formatted file.
    The file must be structured as one generated by L{EffCsvWriter<eff_site.eff.utils.EffCsvWriter>}.
    If there are any external id's for the logs contained in the file being uploaded not found
    on the database, then a form that allows to associate these external id's with
    existing user profiles will be presented to the user
    (see L{eff_admin_users_association<eff_admin_users_association>}).

    @param request: the request object
    @type request: django.core.handlers.wsgi.WSGIRequest

    @return: The django.http.HttpResponse object for the view

    """

    context = {'title' : 'CSV Dump Upload'}

    if request.method == 'POST':
        form = DumpUploadForm(request.POST, request.FILES)
        if form.is_valid():
            n_rows, n_users, n_projects, n_project_assocs, temp_file = load_dump(request.FILES['csv_file'].file)
            if temp_file:
                request.session['log_entries_file'] = temp_file
                request.session['n_users'] = n_users
                return HttpResponseRedirect('/efi/administration/users_association/')
            context['notices'] = ['File Uploaded Sucessfully!']
        else:
            context['errors'] = ['Invalid Form']
    else:
        form = DumpUploadForm()

    context['form'] = form

    return  render_to_response('admin_dump_csv_upload.html', context, context_instance=RequestContext(request))

@login_required
@user_passes_test(__enough_perms, login_url='/accounts/login/')
def eff_fixed_price_client_reports(request):
    if not request.is_ajax():
        context = __get_context(request)
        context['title'] = "Reporte de Clientes - Projectos con costo fijo"
        context['clients'] = Client.objects.filter(project__billing_type='FIXED').distinct()

        if request.method == 'POST':
            client = Client.objects.get(id=request.POST['client'])
            project = Project.objects.get(id=request.POST['project'])

            state_and_country = client.state or ''
            if state_and_country.strip(): state_and_country += ' - '
            state_and_country += client.country
            client_data = {'name' : client.name or '',
                           'address' : client.address or '',
                           'city' : client.city or '',
                           'state_and_country' : state_and_country,
                           'currency' : client.currency.ccy_symbol or client.currency.ccy_code,
                           }
            reverse_billing = FixedPriceClientReverseBilling(
                project_data = {'name' : project.name, 'price' : "%.2f" % project.fixed_price},
                client_data = client_data,
                today = datetime.now().strftime("%A, %d %B %Y")
                )

            basic = Template(source=None, filepath=os.path.join(cur_dir, '../templates/reporte_cliente_precio_fijo.odt'))
            basic_generated = basic.generate(o=reverse_billing).render()
            resp = HttpResponse(basic_generated.getvalue(), mimetype='application/vnd.oasis.opendocument.text')
            cd = 'filename=billing-%s.odt' % project.external_id
            resp['Content-Disposition'] = cd
            return resp

        return render_to_response('admin_reportes_cliente_costo_fijo.html', context)
    else:
        client_id = request.POST['client']
        client = get_object_or_404(Client, id=client_id)
        projects = Project.objects.filter(client=client, billing_type='FIXED')
        ret = '<option selected="selected" value="">----</option>'
        ret += ''.join(['<option value="%s">%s</option>' % (p.id, p.name) for p in projects])
        return HttpResponse(ret, mimetype="text/html")

class UserAssociationsForm(forms.Form):
    """ Dynamic form to associate user external id's with user profiles

    @param users: A list of user external id's (strings)
    @type users: list
    """
    def __init__(self, users, *args, **kwargs):
        super(UserAssociationsForm, self).__init__(*args, **kwargs)
        for user in users:
            self.fields[user] = forms.ModelChoiceField(queryset=UserProfile.objects.all(),
                                                       empty_label="----",
                                                       label=user)
@login_required
@user_passes_test(__enough_perms, login_url='/accounts/login/')
def eff_admin_users_association(request):
    """ Allows to associate users external id's that not exists in the database
    with existant user profiles.
    This view expect a path to an Eff formatted csv file
    (see L{EffCsvWriter<eff_site.eff.utils.EffCsvWriter>}) and a list of user profiles
    in session variables. When the external id's with user profile associations is
    submited, the external id's are created and the logs on the csv file are imported
    to the system.

    @param request: the request object
    @type request: django.core.handlers.wsgi.WSGIRequest

    @return: The django.http.HttpResponse object for the view

    """

    context = {'title' : 'Asociación de usuarios'}
    if 'log_entries_file' in request.session and 'n_users' in request.session:
        n_users = request.session['n_users']
        log_entries_file = request.session['log_entries_file']
        form = UserAssociationsForm(n_users)
        context.update({'n_users' : n_users,
                        'user_profiles' : map(lambda e: e.login, ExternalId.objects.all())})
    else:
        return HttpResponseRedirect('/efi/administration/dump-csv-upload/')

    if request.method == 'POST':
        form = UserAssociationsForm(n_users, request.POST)
        if form.is_valid():
            r_file = open(log_entries_file, 'r')

            ext_src, client, author, from_date, to_date = validate_header(r_file)

            external_source = ExternalSource.objects.get(name=ext_src)
            dumps = Dump.objects.filter(date=date.today(),
                                        creator=author,
                                        source=external_source)
            if dumps:
                dump = dumps[0]
            else:
                dump = Dump.objects.create(date=date.today(),
                                           creator=author,
                                           source=external_source)
            rows = []
            temp_reader = csv.reader(r_file)

            for row in temp_reader:
                u_p = UserProfile.objects.get(id=request.POST[row[2]])
                e_i, created = ExternalId.objects.get_or_create(userprofile=u_p, login=row[2],
                                                                source=external_source)
                row[2] = e_i.login
                rows.append(row)

            r_file.close()

            for row in rows:
                user = UserProfile.objects.filter(externalid__login=row[2])[0].user
                d = _date_fmts(row[0])
                t_proj = Project.objects.get(external_id=row[1])

                tl_dict = {'date' : d,
                           'project' : t_proj,
                           'task_name' : row[4],
                           'user' : user,
                           'hours_booked' : row[3],
                           'description' : row[5],
                           'dump' : dump
                           }
                TimeLog.objects.create(**tl_dict)

            del request.session['log_entries_file']
            del request.session['n_users']

            context['notices'] = ['File Uploaded Sucessfully!']

        else:
            context['errors'] = ['Invalid Form']

    context['form'] = form

    return render_to_response('admin_users_association.html', context, context_instance=RequestContext(request))
