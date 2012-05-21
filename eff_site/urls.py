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

from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
from django.views.generic.simple import redirect_to
from django.views.static import serve

from django.contrib import admin
admin.autodiscover()

from eff_site.settings import CURRENT_ABS_DIR
from eff_site.eff.views import update_hours, eff, eff_check_perms,\
    eff_previous_week, eff_current_week, eff_current_month, eff_horas_extras,\
    eff_chart, eff_next, eff_prev, eff_charts, eff_report, eff_update_db,\
    eff_administration, eff_client_report, eff_client_reports_admin, \
    UserProfileForm, eff_last_month, eff_admin_add_user, \
    eff_admin_change_profile, profile_detail, eff_dump_csv_upload, \
    eff_fixed_price_client_reports, eff_admin_users_association

from os.path import join

jscalendar_dir = join(CURRENT_ABS_DIR, 'addons/jscalendar-1.0/')
js_dir = join(CURRENT_ABS_DIR, 'addons/js/')
jscalendar_lang_dir = join(CURRENT_ABS_DIR, 'addons/jscalendar-1.0/lang/')
calendar_dir = join(CURRENT_ABS_DIR, 'addons/simple-calendar/')
sortable_dir = join(CURRENT_ABS_DIR, 'addons/sortable-table/')
templates_dir = join(CURRENT_ABS_DIR, 'templates/')
images_dir = join(CURRENT_ABS_DIR, 'templates/images/')

urlpatterns = patterns('',
    (r'^$', redirect_to, {'url': '/efi/semanaactual/'}),
    # django-profiles
    url(r'^accounts/login/$', login, {'template_name': 'login.html'},
        name='login'),
    url(r'^accounts/logout/$', logout, {'template_name': 'logout.html'},
        name='logout'),
    (r'^accounts/profile/$', redirect_to, {'url': '/efi/semanaactual/'}),
    (r'^login/$', redirect_to, {'url': '/accounts/login/'}),
    (r'^logout/$', redirect_to, {'url': '/accounts/logout/'}),
    (r'^checkperms/([A-Za-z_0-9]*)/$', eff_check_perms),
    url(r'^profiles/edit', 'profiles.views.edit_profile',
        {'form_class': UserProfileForm, }, name='profiles_edit'),
    (r'^profiles/(?P<username>[\w\._-]+)/$', profile_detail),
    (r'^profiles/', include('profiles.urls')),
    (r'^updatehours/([A-Za-z_0-9]*)/$', update_hours),
    (r'^efi/$', eff),
    (r'^efi/semanaanterior/$', eff_previous_week),
    (r'^efi/semanaactual/$', eff_current_week),
    (r'^efi/mesactual/$', eff_current_month),
    (r'^efi/mespasado/$', eff_last_month),
    (r'^efi/horasextras/$', eff_horas_extras),
    (r'^efi/next/$', eff_next),
    (r'^efi/prev/$', eff_prev),
    (r'^efi/chart/([A-Za-z_0-9]*)/$', eff_chart),
    (r'^efi/charts/$', eff_charts),
    (r'^efi/reporte/([A-Za-z_0-9]*)/$', eff_report),
    (r'^efi/update-db/$', eff_update_db),
    (r'^js/(?P<path>.*)$', serve, {'document_root': js_dir}),
    (r'^jscalendar/(?P<path>.*)$', serve, {'document_root': jscalendar_dir}),
    (r'^jscalendar/lang/(?P<path>.*)$', serve,
        {'document_root': jscalendar_lang_dir}),
    (r'^simple-calendar/(?P<path>.*)$', serve, {'document_root': calendar_dir}),
    (r'^sortable/(?P<path>.*)$', serve, {'document_root': sortable_dir}),
    (r'^templates/(?P<path>.*)$', serve, {'document_root': templates_dir}),
    (r'^images/(?P<path>.*)$', serve, {'document_root': images_dir}),
    (r'^efi/administration/users_password/$', eff_administration),
    (r'^efi/administration/users_profile/$', eff_admin_change_profile),
    (r'^efi/administration/add_user/$', eff_admin_add_user),
    (r'^efi/administration/client_reports/$', eff_client_reports_admin),
    (r'^efi/administration/fixed_price_client_reports/$',
        eff_fixed_price_client_reports),
    (r'^efi/administration/dump-csv-upload/$', eff_dump_csv_upload),
    (r'^efi/reporte_cliente/([-\w]+)/$', eff_client_report),
    (r'^efi/administration/users_association/$', eff_admin_users_association),
    url(r'^admin/', include(admin.site.urls)),
)
