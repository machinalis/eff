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

from django.contrib import admin
from eff_site.eff.models import Project, Client, ExternalSource, Wage, BillingEmail
from eff_site.eff.models import AvgHours, Currency, ProjectAssoc, TimeLog
from eff_site.eff.models import Handle, ClientHandles
from _models.user_profile import UserProfile
from eff_site.eff.forms import UserAdminForm
from django.contrib.auth.models import User
from _models.dump import Dump
from eff_site.eff._models.external_source import ExternalId
from django import forms


class TimeLogAdminForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.order_by('username'))
    dump = forms.ModelChoiceField(queryset=Dump.objects.order_by('-date'))

    class Meta:
        model = TimeLog


class TimeLogAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'hours_booked', 'project', 'task_name',
                    'description')
    ordering = ('date',)
    search_fields = ('task_name', 'description', 'user__username',
                     'user__first_name')
    form = TimeLogAdminForm


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'billable', 'client', 'external_id')
    ordering = ('name',)
    search_fields = ('name',)


class ProjectAssocAdmin(admin.ModelAdmin):
    list_display = ('project', 'member', 'from_date', 'to_date', 'client_rate',
                    'user_rate', )
    ordering = ('member',)
    search_fields = ('project__name', 'member__user__username',
                     'member__user__first_name')


class ProjectsInline(admin.TabularInline):
    model = Project
    extra = 1


class BillingEmailAdminForm(forms.ModelForm):
    client = forms.ModelChoiceField(queryset=Client.objects.order_by('name'))

    class Meta:
        model = BillingEmail


class BillingEmailAdmin(admin.ModelAdmin):
    search_fields = ('email_address', 'client__name', )
    ordering = ('client',)
    list_display = ('client', 'email_address', 'send_as')
    list_filter = ('client', 'email_address', 'send_as')
    form = BillingEmailAdminForm


class BillingEmailsInLine(admin.TabularInline):
    model = BillingEmail
    extra = 1


class ClientAdmin(admin.ModelAdmin):
    inlines = [BillingEmailsInLine, ProjectsInline]
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'city', 'country',
                     'currency__ccy_code', 'external_source__name',)
    ordering = ('name',)


class ExternalSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'fetch_url', 'csv_directory', 'csv_filename')
    ordering = ('name',)
    #inlines = [ProjectsInline2]


class WageInLine(admin.TabularInline):
    model = Wage


class WageAdminForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.order_by('username'))

    class Meta:
        model = Wage


class WageAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'amount_per_hour')
    list_filter = ('date', 'amount_per_hour',)
    ordering = ('date',)
    search_fields = ('user__first_name', 'user__username',)
    form = WageAdminForm


class AvgHoursInLine(admin.TabularInline):
    model = AvgHours


class AvgHoursAdminForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.order_by('username'))

    class Meta:
        model = AvgHours


class AvgHoursAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'hours')
    list_filter = ('date', 'hours',)
    ordering = ('-date',)
    search_fields = ('user__first_name', 'user__username',)
    form = AvgHoursAdminForm


class UserProfileInLine(admin.TabularInline):
    model = UserProfile


class UserProfileAdminForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.order_by('username'))
    # Set amount of users shown at a time to 10, make an ordered query
    watches = forms.ModelMultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'size': 10}),
        queryset=User.objects.order_by('username'),
        label='Users to follow', required=False)

    def clean_watches(self):
        data = self.cleaned_data['watches']
        try:
            admin_user = User.objects.get(username='admin')
        except User.DoesNotExist:
            pass
        else:
            if admin_user in data:
                raise forms.ValidationError("Don't add admin here")

        if self.instance.user in data:
            raise forms.ValidationError("You are adding this user to watch " +\
                                        "himself, please don't")

        return data

    class Meta:
        model = UserProfile


class ClientHandlesInline(admin.TabularInline):
    model = ClientHandles


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'phone_number')
    ordering = ('user__username',)
    search_fields = ('user__first_name', 'user__username',)
    form = UserProfileAdminForm
    inlines = [ClientHandlesInline]


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name')
    inlines = [WageInLine, AvgHoursInLine]
    ordering = ('username',)
    form = UserAdminForm


class CurrencyAdmin(admin.ModelAdmin):
    pass


class ExternalIdAdmin(admin.ModelAdmin):
    list_display = ('login', 'source', 'userprofile')
    search_fields = ('userprofile__user__username',
                     'userprofile__user__first_name')
    ordering = ('userprofile',)


class HandleAdmin(admin.ModelAdmin):
    list_display = ('protocol',)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectAssoc, ProjectAssocAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(ExternalSource, ExternalSourceAdmin)
admin.site.register(Wage, WageAdmin)
admin.site.register(AvgHours, AvgHoursAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(ExternalId, ExternalIdAdmin)
admin.site.register(TimeLog, TimeLogAdmin)
admin.site.register(BillingEmail, BillingEmailAdmin)
admin.site.register(Handle, HandleAdmin)
