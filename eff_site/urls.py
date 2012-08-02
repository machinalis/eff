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
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

from eff_site.settings import CURRENT_ABS_DIR
from eff_site.eff.views import (update_hours, eff, eff_check_perms,
    eff_previous_week, eff_current_week, eff_current_month, eff_horas_extras,
    eff_chart, eff_next, eff_prev, eff_charts, eff_report, eff_update_db,
    eff_administration, eff_client_report, eff_client_reports_admin,
    UserProfileForm, eff_last_month, eff_admin_add_user,
    eff_admin_change_profile, profile_detail, eff_dump_csv_upload,
    eff_fixed_price_client_reports, eff_admin_users_association, eff_home,
    eff_client_home, index, eff_client_projects, eff_client_summary,
    eff_client_summary_period)

from os.path import join

jscalendar_dir = join(CURRENT_ABS_DIR, 'addons/jscalendar-1.0/')
js_dir = join(CURRENT_ABS_DIR, 'addons/js/')
jscalendar_lang_dir = join(CURRENT_ABS_DIR, 'addons/jscalendar-1.0/lang/')
calendar_dir = join(CURRENT_ABS_DIR, 'addons/simple-calendar/')
sortable_dir = join(CURRENT_ABS_DIR, 'addons/sortable-table/')
templates_dir = join(CURRENT_ABS_DIR, 'templates/')
images_dir = join(CURRENT_ABS_DIR, 'templates/images/')

urlpatterns = patterns('',
    url(r'^$', index, name='root'),
    url(r'^clients/home/$', eff_client_home, name='client_home'),
    url(r'^clients/projects/$', eff_client_projects, name='client_projects'),
    url(r'^clients/summary/period/$', eff_client_summary_period,
        name='client_summary_period'),
    url(r'^clients/summary/$', eff_client_summary,
        name='client_summary'),
    # django-profiles
    url(r'^accounts/login/$', login, {'template_name': 'login.html'},
        name='login'),
    url(r'^accounts/logout/$', logout, {'template_name': 'logout.html'},
        name='logout'),
    url(r'^accounts/profile/$', eff_home, name='eff_home'),
    url(r'^login/$', redirect_to, {'url': '/accounts/login/'},
        name='redir_login'),
    url(r'^logout/$', redirect_to, {'url': '/accounts/logout/'},
        name='redir_logout'),
    url(r'^checkperms/([A-Za-z_0-9]*)/$', eff_check_perms, name='checkperms'),
    url(r'^profiles/edit', 'eff.views.edit_profile',
        {'form_class': UserProfileForm, }, name='profiles_edit'),
    url(r'^profiles/(?P<username>[\w\._-]+)/$', profile_detail,
        name='profiles_detail'),
    url(r'^profiles/', include('profiles.urls'), name='profiles'),
    # password reset
    url(r'^accounts/password_reset/$',
        'django.contrib.auth.views.password_reset',
        {'template_name': 'password_reset.html',
         'email_template_name': 'password_reset_email.html'},
        name='password_reset'),
    url(r'^password_reset/$', redirect_to,
        {'url': '/accounts/password_reset/'}, name='redir_password_reset'),
    url(r'^accounts/password_reset/done/$',
        'django.contrib.auth.views.password_reset_done',
        {'template_name': 'password_reset_done.html'},
        name='password_reset_done'),
    url(r'^accounts/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'template_name': 'password_reset_confirm.html'},
        name='password_reset_confirm'),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        redirect_to,
        {'url': '/accounts/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/'},
        name='redir_password_reset_confirm'),
    url(r'^accounts/reset/done/$',
        'django.contrib.auth.views.password_reset_complete',
        {'template_name': 'password_reset_complete.html'},
        name='password_reset_complete'),
    # password change
    url(r'^accounts/change_password/$',
        'django.contrib.auth.views.password_change',
        {'template_name': 'password_change.html',
         'post_change_redirect': '/accounts/change_password/done/'},
        name='password_change'),
    url(r'^accounts/change_password/done/$',
        'django.contrib.auth.views.password_change_done',
        {'template_name': 'password_change_done.html'},
        name='password_change_done'),
    url(r'^password_change/$', redirect_to,
        {'url': '/accounts/password_change/'},
        name='redir_password_change'),
    url(r'^updatehours/([A-Za-z_0-9]*)/$', update_hours, name='update_hours'),
    url(r'^efi/$', eff, name='eff'),
    url(r'^efi/semanaanterior/$', eff_previous_week, name='eff_previous_week'),
    url(r'^efi/semanaactual/$', eff_current_week, name='eff_current_week'),
    url(r'^efi/mesactual/$', eff_current_month, name='eff_current_month'),
    url(r'^efi/mespasado/$', eff_last_month, name='eff_last_month'),
    url(r'^efi/horasextras/$', eff_horas_extras, name='eff_extra_hours'),
    url(r'^efi/next/$', eff_next, name='eff_next'),
    url(r'^efi/prev/$', eff_prev, name='eff_prev'),
    url(r'^efi/chart/([A-Za-z_0-9]*)/$', eff_chart, name='eff_chart'),
    url(r'^efi/charts/$', eff_charts, name='eff_charts'),
    url(r'^efi/reporte/([A-Za-z_0-9]*)/$', eff_report, name='eff_report'),
    url(r'^efi/update-db/$', eff_update_db, name='eff_update_db'),
    (r'^js/(?P<path>.*)$', serve, {'document_root': js_dir}),
    (r'^jscalendar/(?P<path>.*)$', serve, {'document_root': jscalendar_dir}),
    (r'^jscalendar/lang/(?P<path>.*)$', serve,
        {'document_root': jscalendar_lang_dir}),
    (r'^simple-calendar/(?P<path>.*)$', serve, {'document_root': calendar_dir}),
    (r'^sortable/(?P<path>.*)$', serve, {'document_root': sortable_dir}),
    (r'^templates/(?P<path>.*)$', serve, {'document_root': templates_dir}),
    (r'^images/(?P<path>.*)$', serve, {'document_root': images_dir}),
    url(r'^efi/administration/users_password/$', eff_administration,
        name='eff_administration'),
    url(r'^efi/administration/users_profile/$', eff_admin_change_profile,
        name='eff_admin_change_profile'),
    url(r'^efi/administration/add_user/$', eff_admin_add_user,
        name='eff_admin_add_user'),
    url(r'^efi/administration/client_reports/$', eff_client_reports_admin,
        name='eff_client_reports_admin'),
    url(r'^efi/administration/fixed_price_client_reports/$',
        eff_fixed_price_client_reports, name='eff_fixed_price_client_reports'),
    url(r'^efi/administration/dump-csv-upload/$', eff_dump_csv_upload,
        name='eff_dump_csv_upload'),
    url(r'^efi/reporte_cliente/([-\w]+)/$', eff_client_report,
        name='eff_client_report'),
    url(r'^efi/administration/users_association/$',
        eff_admin_users_association, name='eff_admin_users_association'),
    url(r'^efi/administration/client_summary/$',
        eff_client_summary_period,
        name='eff_client_summary_period'),
    url(r'^efi/administration/client_summary/([-\w]+)/$',
        eff_client_summary,
        name='eff_client_summary'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^attachments/', include('attachments.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^attachments/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': join(CURRENT_ABS_DIR, 'attachments'),
        }),
   )
