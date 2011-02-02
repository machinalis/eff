from django.contrib import admin
from sitio.eff.models import Project, Client, ExternalSource, Wage
from sitio.eff.models import AvgHours, Currency, ProjectAssoc, TimeLog
from _models.user_profile import *
from sitio.eff._models.external_source import ExternalId

class TimeLogAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'hours_booked', 'project', 'task_name', 'description')
    ordering = ('date', 'project__name')
    search_fields = ('task_name', 'description', 'user__username', 'user__first_name')

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'billable', 'client', 'external_id')
    ordering = ('name', 'billable',)
    search_fields = ('name',)

class ProjectAssocAdmin(admin.ModelAdmin):
    list_display = ('project', 'member', 'from_date', 'to_date', 'client_rate', 'user_rate', )
    ordering = ('project', 'member',)
    search_fields = ('project__name', 'member__user__username',
                     'member__user__first_name')

class ProjectsInline(admin.TabularInline):
    model = Project
    extra = 1

class ClientAdmin(admin.ModelAdmin):
    inlines = [ProjectsInline]
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'city', 'country',
                     'currency__ccy_code', 'external_source__name',)
                     

class ExternalSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'fetch_url', 'csv_directory', 'csv_filename')
    ordering = ('name',)
    #inlines = [ProjectsInline2]

class WageInLine(admin.TabularInline):
    model = Wage

class WageAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'amount_per_hour')
    list_filter = ('date', 'amount_per_hour',)
    ordering = ('date',)
    search_fields = ('user__first_name', 'user__username',)

class AvgHoursInLine(admin.TabularInline):
    model = AvgHours

class AvgHoursAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'hours')
    list_filter = ('date', 'hours',)
    ordering = ('date',)
    search_fields = ('user__first_name', 'user__username',)

class UserProfileInLine(admin.TabularInline):
    model = UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'phone_number')
    ordering = ('user',)
    search_fields = ('user__first_name', 'user__username',)

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name')
    ordering = ('username',)
    inlines = [WageInLine, AvgHoursInLine]

class CurrencyAdmin(admin.ModelAdmin):
    pass

class ExternalIdAdmin(admin.ModelAdmin):
    list_display = ('login', 'source', 'userprofile') 
    search_fields = ('userprofile__user__username',
                     'userprofile__user__first_name')


#admin.site.register(User, UserAdmin)
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
