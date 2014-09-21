from ecwsp.volunteer_track.models import *
from django.contrib import admin
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
import autocomplete_light

import datetime

def approve_site(modeladmin, request, queryset):
    queryset.update(site_approval = 'Accepted')
    for object in queryset:
        LogEntry.objects.log_action(
                    user_id         = request.user.pk, 
                    content_type_id = ContentType.objects.get_for_model(object).pk,
                    object_id       = object.pk,
                    object_repr     = unicode(object), 
                    action_flag     = CHANGE
                )
    
def reject_site(modeladmin, request, queryset):
    queryset.update(site_approval = 'Rejected')
    for object in queryset:
        LogEntry.objects.log_action(
                    user_id         = request.user.pk, 
                    content_type_id = ContentType.objects.get_for_model(object).pk,
                    object_id       = object.pk,
                    object_repr     = unicode(object), 
                    action_flag     = CHANGE
                )
    
def time_fulfilled(modeladmin, request, queryset):
    queryset.update(hours_confirmed=True)
    for object in queryset:
        hrsInstance = Hours(student=object.student, date =  date.today)
        if object.hours_completed():
            if object.hours_completed() < object.hours_required:
                hrsInstance.hours = (object.hours_required) - (object.hours_completed())
                
        else:
            hrsInstance.hours = object.hours_required
        hrsInstance.save()
    LogEntry.objects.log_action(
                    user_id         = request.user.pk, 
                    content_type_id = ContentType.objects.get_for_model(object).pk,
                    object_id       = object.pk,
                    object_repr     = unicode(object), 
                    action_flag     = CHANGE
                )        


class HoursInline(admin.TabularInline):
    model = Hours
    extra = 1

class VolunteerSiteInline(admin.StackedInline):
    model = VolunteerSite
    extra = 1

class VolunteerSiteAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(VolunteerSite)
    list_display = ('volunteer','supervisor','site_approval','contract','hours_confirmed','inactive')
    actions = [approve_site,reject_site,time_fulfilled]
    inlines = [HoursInline]
admin.site.register(VolunteerSite,VolunteerSiteAdmin)

class VolunteerAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Volunteer)
    list_display = ('student','hours_required','hours_completed')
    list_filter = ['sites', 'student',]
    search_fields = ['student__first_name', 'student__last_name',]
    inlines = [VolunteerSiteInline]
admin.site.register(Volunteer,VolunteerAdmin)


class SiteSupervisorInline(admin.TabularInline):
    model = SiteSupervisor
    extra = 0    

class SiteAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'site_address')
    search_fields = ['site_name', 'site_address', 'site_city', 'site_zip', 'site_state']
    inlines = [SiteSupervisorInline]
    
admin.site.register(Site, SiteAdmin)

class SiteSupervisorAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')
    search_fields = ['name', 'phone', 'email', 'site__site_name', 'site__site_address', 'site__site_city', 'site__site_zip', 'site__site_state']
admin.site.register(SiteSupervisor,SiteSupervisorAdmin)


